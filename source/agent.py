import numpy
import pygame

from source.brain import Brain
from source.constants import SCAN_RADIUS, AGENT_SIZE, RABBIT_COLOR, RABBIT_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT, \
    RABBIT_NUMBER, GRASS_NUMBER, FOOD_COLOR, FOOD_SPEED, FOOD_NUMBER, FOX_NUMBER, \
    FOX_SPEED, FOX_COLOR, SCAN_DIAMETER
from source.utils import get_random_coordinate, SCAN_MASKS


class Agent:
    def __init__(self, name: str, color: tuple[int, int, int], speed: float, number: int,
                 start_coordinates: tuple[float, float],
                 brain: Brain | None, world: dict[tuple[float, float], ...], die_threshold: tuple[int, int],
                 food_threshold: int) -> None:
        self._name_ = name
        self._color_ = color
        self._speed_ = speed
        self._brain_ = brain
        self._world_ = world
        self._number_ = number
        self._to_die_threshold_ = numpy.random.randint(die_threshold[0], die_threshold[1])
        self._food_threshold_ = food_threshold
        self._previous_move_ = -1
        self._same_moves_counter_ = 0

        self._area_ = numpy.zeros(SCAN_DIAMETER ** 2, dtype=numpy.float32)
        self._previous_area_ = numpy.zeros(SCAN_DIAMETER ** 2, dtype=numpy.float32)
        self._rect_ = pygame.Rect(start_coordinates, (AGENT_SIZE, AGENT_SIZE))

        self._old_position_ = [0, 0]
        self._fps_counter_ = 0
        self._food_counter_ = 0
        self._to_die_counter_ = 0
        self._food_eaten_ = 0

        self._dead_ = False
        self._reproduce_ = False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self._color_, self._rect_)

    def scan_area(self) -> None:
        x, y = self.position

        for i, xi in enumerate(range(x - SCAN_RADIUS, x + SCAN_RADIUS + 1)):
            for j, yj in enumerate(range(y - SCAN_RADIUS, y + SCAN_RADIUS + 1)):
                self._area_[i * SCAN_DIAMETER + j] = int(self._world_.get((xi, yj), GRASS_NUMBER))

    def handle_collision(self, item: ...) -> None:
        ...

    def move(self) -> None:
        self.step()

        if self._fps_counter_ % (10 // self._speed_) == 0:
            self.scan_area()
            move = self._brain_.forward(self._area_) + 1

            x, y = self.position

            match move:
                case 1:
                    self.handle_collision(self._world_.get((x - 1, y), 0))
                    self._to_die_counter_ += 1

                    if self._rect_.x < 0:
                        self._dead_ = True

                    self._rect_.x -= 1
                case 2:
                    self.handle_collision(self._world_.get((x, y - 1), 0))
                    self._to_die_counter_ += 1

                    if self._rect_.y < 0:
                        self._dead_ = True

                    self._rect_.y -= 1
                case 3:
                    self.handle_collision(self._world_.get((x + 1, y), 0))
                    self._to_die_counter_ += 1

                    if self._rect_.x > SCREEN_WIDTH:
                        self._dead_ = True

                    self._rect_.x += 1
                case 4:
                    self.handle_collision(self._world_.get((x, y + 1), 0))
                    self._to_die_counter_ += 1

                    if self._rect_.y > SCREEN_HEIGHT:
                        self._dead_ = True

                    self._rect_.y += 1
                # case 5:
                #     self._to_die_counter_ += 0.25
                #     return
                case 5:
                    self.handle_collision(self._world_.get((x - 1, y - 1), 0))
                    self._to_die_counter_ += 1

                    if self._rect_.y < 0 or self._rect_.x < 0:
                        self._dead_ = True

                    self._rect_.y -= 1
                    self._rect_.x -= 1

                    return
                case 6:
                    self.handle_collision(self._world_.get((x + 1, y - 1), 0))
                    self._to_die_counter_ += 1

                    if self._rect_.y < 0 or self._rect_.x > SCREEN_WIDTH:
                        self._dead_ = True

                    self._rect_.y -= 1
                    self._rect_.x += 1

                    return
                case 7:
                    self.handle_collision(self._world_.get((x + 1, y + 1), 0))
                    self._to_die_counter_ += 1

                    if self._rect_.y > SCREEN_HEIGHT or self._rect_.x > SCREEN_WIDTH:
                        self._dead_ = True

                    self._rect_.y += 1
                    self._rect_.x += 1

                    return
                case 8:
                    self.handle_collision(self._world_.get((x - 1, y + 1), 0))
                    self._to_die_counter_ += 1

                    if self._rect_.y > SCREEN_HEIGHT or self._rect_.x < 0:
                        self._dead_ = True

                    self._rect_.x -= 1
                    self._rect_.y += 1

                    return

            # if self._world_.get((x, y), 0) is self:
            #     self._world_[(x, y)] = GRASS_NUMBER
            #
            # self._world_[self.position] = self

    def step(self) -> None:
        self._fps_counter_ += 1

        if self._to_die_counter_ >= self._to_die_threshold_:
            self._dead_ = True
        elif self._food_counter_ >= self._food_threshold_:
            self._reproduce_ = True

    def die(self) -> None:
        self._dead_ = True

    def eat(self) -> None:
        self._food_counter_ += 1
        self._food_eaten_ += 1

    def reproduce_done(self) -> None:
        self._reproduce_ = False
        self._food_counter_ = 0

    @property
    def position(self) -> tuple[float, float]:
        return self._rect_.topleft

    @position.setter
    def position(self, value: tuple[float, float]) -> None:
        self._rect_.topleft = value

    @property
    def is_dead(self) -> bool:
        return self._dead_

    @property
    def can_reproduce(self) -> bool:
        return self._reproduce_

    @property
    def brain(self) -> Brain:
        return self._brain_

    @brain.setter
    def brain(self, brain: Brain) -> None:
        self._brain_ = brain

    @property
    def food_eaten(self) -> int:
        return self._food_eaten_

    def __int__(self) -> int:
        return self._number_


class Rabbit(Agent):
    def __init__(self, world: dict[tuple[float, float], Agent]):
        super().__init__("rabbit", RABBIT_COLOR, RABBIT_SPEED, RABBIT_NUMBER,
                         get_random_coordinate(), Brain(), world, (250, 300), 3)

    def scan_area(self) -> None:
        x, y = self.position

        for i, xi in enumerate(range(x - SCAN_RADIUS, x + SCAN_RADIUS + 1)):
            for j, yj in enumerate(range(y - SCAN_RADIUS, y + SCAN_RADIUS + 1)):
                if xi < 0 or xi > SCREEN_WIDTH or yj < 0 or yj > SCREEN_HEIGHT:
                    self._area_[i * SCAN_DIAMETER + j] = -1
                    continue

                value = int(self._world_.get((xi, yj), GRASS_NUMBER))

                if value == FOX_NUMBER:
                    self._area_[i * SCAN_DIAMETER + j] = -1
                elif value == FOOD_NUMBER:
                    self._area_[i * SCAN_DIAMETER + j] = 1
                elif value == GRASS_NUMBER:
                    self._area_[i * SCAN_DIAMETER + j] = 0
                elif value == RABBIT_NUMBER:
                    self._area_[i * SCAN_DIAMETER + j] = 0

        if self._fps_counter_ > 0:
            self.brain.calculate_reward([sum(self._area_[mask] - self._previous_area_[mask]) for mask in SCAN_MASKS])

            numpy.copyto(self._previous_area_, self._area_)
        else:
            numpy.copyto(self._previous_area_, self._area_)

    def handle_collision(self, item: ...) -> None:
        if int(item) == FOOD_NUMBER:
            self._food_counter_ += 1
            self._food_eaten_ += 1
            self._to_die_counter_ = 0

            self.brain.reward_once()

            item.die()
        elif int(item) == FOX_NUMBER:
            self.die()
            item.eat()


class Food(Agent):
    def __init__(self, world: dict[tuple[float, float], ...]):
        super().__init__("food", FOOD_COLOR, FOOD_SPEED, FOOD_NUMBER, get_random_coordinate(), None, world, (45, 155),
                         1)

    def step(self) -> None:
        self._fps_counter_ += 1
        self._to_die_counter_ += 1

        if self._fps_counter_ % 50 == 0:
            self._food_counter_ += 1

        if self._to_die_counter_ >= self._to_die_threshold_:
            self._dead_ = True
        elif self._food_counter_ >= self._food_threshold_:
            self._reproduce_ = True

    def move(self) -> None:
        self.step()

    def scan_area(self) -> None:
        return


class Fox(Agent):
    def __init__(self, world: dict[tuple[float, float], ...]):
        super().__init__("fox", FOX_COLOR, FOX_SPEED, FOX_NUMBER, get_random_coordinate(), Brain(), world,
                         (400, 600), 1)

    def scan_area(self) -> None:
        x, y = self.position

        for i, xi in enumerate(range(x - SCAN_RADIUS, x + SCAN_RADIUS + 1)):
            for j, yj in enumerate(range(y - SCAN_RADIUS, y + SCAN_RADIUS + 1)):
                if xi < 0 or xi > SCREEN_WIDTH or yj < 0 or yj > SCREEN_HEIGHT:
                    self._area_[i * SCAN_DIAMETER + j] = -1
                    continue

                value = int(self._world_.get((xi, yj), GRASS_NUMBER))

                if value == FOX_NUMBER:
                    self._area_[i * SCAN_DIAMETER + j] = 0
                elif value == FOOD_NUMBER:
                    self._area_[i * SCAN_DIAMETER + j] = 0
                elif value == GRASS_NUMBER:
                    self._area_[i * SCAN_DIAMETER + j] = 0
                elif value == RABBIT_NUMBER:
                    self._area_[i * SCAN_DIAMETER + j] = 1

        if self._fps_counter_ > 0:
            self.brain.calculate_reward([sum(self._area_[mask] - self._previous_area_[mask]) for mask in SCAN_MASKS])

            numpy.copyto(self._previous_area_, self._area_)
        else:
            numpy.copyto(self._previous_area_, self._area_)

    def handle_collision(self, item: ...) -> None:
        if int(item) == RABBIT_NUMBER:
            self._food_counter_ += 1
            self._food_eaten_ += 1
            self._to_die_counter_ = 0

            self.brain.reward_once()

            item.die()
