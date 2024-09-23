import random
import sys
from typing import Callable

import matplotlib.pyplot as plt
import pygame

pygame.init()
pygame.font.init()

from source.agent import Rabbit, Agent, Food, Fox
from source.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_WIDTH, WINDOW_HEIGHT, GRASS_COLOR, \
    REFILL_WORLD_THRESHOLD, DECAY, REFILL_WORLD_EPOCH_THRESHOLD
from source.utils import get_random_coordinate


class Simulation:
    def __init__(self, rabbits_number: int, foxes_number: int, food_number: int) -> None:
        self._screen_ = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._display_ = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self._clock_ = pygame.time.Clock()

        self._rabbits_number_ = rabbits_number
        self._foxes_number_ = foxes_number
        self._food_number_ = food_number

        self._agents_: list[Agent, ...] | list = []
        self._agents_position_: dict[tuple[float, float], Agent | int] = {}
        self._epoch_ = 0
        self._fox_refills_ = 0
        self._rabbit_refills_ = 0
        self._rabbit_refill_threshold_ = REFILL_WORLD_THRESHOLD
        self._rabbit_epochs_refill_threshold_ = REFILL_WORLD_EPOCH_THRESHOLD
        self._fox_refill_threshold_ = REFILL_WORLD_THRESHOLD
        self._fox_epochs_refill_threshold_ = REFILL_WORLD_EPOCH_THRESHOLD

        self._font_ = pygame.font.SysFont("Arial", 24)

        self._last_rabbit_ = None
        self._last_fox_ = None

        self._counters_ = {
            "food": [],
            "rabbit": [],
            "fox": [],
        }

    def __del__(self) -> None:
        self.draw_end()

    def draw_end(self) -> None:
        plt.plot(self._counters_.get("food"), label="Food", color="green")
        plt.plot(self._counters_.get("rabbit"), label="Rabbit", color="gray")
        plt.plot(self._counters_.get("fox"), label="Fox", color="orange")

        plt.grid()
        plt.legend()
        plt.show()

    def fill_unit(self, class_to_fill: Callable, range_to_fill: int, reference_unit: Agent = None) -> None:
        for index in range(range_to_fill):
            unit = class_to_fill(self._agents_position_)

            if reference_unit:
                unit.brain.load_state_dict(reference_unit.brain.state_dict())

                if isinstance(reference_unit, Rabbit):
                    unit.brain.mutate(self._rabbit_refills_ * DECAY / 2)
                elif isinstance(reference_unit, Fox):
                    unit.brain.mutate(self._fox_refills_ * DECAY / 2)

            while self._agents_position_.get(unit.position, 0):
                unit.position = get_random_coordinate()

            self._agents_.append(unit)
            self._agents_position_[unit.position] = unit

    def fill_particular_unit(self, unit: Agent, center_position: tuple[int, int]) -> None:
        # while self._agents_position_.get(unit.position, 0):
        #     unit.position = get_random_coordinate()

        unit.position = (center_position[0] + random.randint(-7, 7), center_position[1] + random.randint(-7, 7))

        self._agents_.append(unit)
        self._agents_position_[unit.position] = unit

    def fill_world(self) -> None:
        self.fill_unit(Rabbit, self._rabbits_number_, self._last_rabbit_)
        self.fill_unit(Food, self._food_number_)
        self.fill_unit(Fox, self._foxes_number_, self._last_fox_)

    def clear_world(self) -> None:
        self._agents_.clear()
        self._agents_position_.clear()
        self._epoch_ = 0
        self._last_fox_ = None
        self._last_rabbit_ = None

    def draw_world(self) -> None:
        self._screen_.fill(GRASS_COLOR)

        for agent in self._agents_:
            agent.draw(self._screen_)

    def move_agents(self) -> None:
        for agent in self._agents_:
            agent.move()

        self._agents_position_.clear()

        for agent in self._agents_:
            self._agents_position_[agent.position] = agent

    def check_dead(self) -> None:
        for agent in self._agents_:
            if agent.is_dead:
                self._agents_.remove(agent)

                if agent.position in self._agents_position_:
                    self._agents_position_[agent.position] = 0
            elif agent.position not in self._agents_position_:
                self._agents_.remove(agent)

    def check_reproduce(self) -> None:
        for agent in self._agents_:
            if agent.can_reproduce:
                new_agent = type(agent)(self._agents_position_)

                if new_agent.position in self._agents_position_:
                    continue

                if new_agent.brain:
                    new_agent.brain.load_state_dict(agent.brain.state_dict())
                    new_agent.brain.mutate(self._epoch_)

                self.fill_particular_unit(new_agent, agent.position)

                # self._agents_position_[new_agent.position] = new_agent
                # self._agents_.append(new_agent)

                agent.reproduce_done()

    def count_agents(self) -> None:
        food_counter = 0
        fox_counter = 0
        rabbit_counter = 0

        for agent in self._agents_:
            if isinstance(agent, Food):
                food_counter += 1
            elif isinstance(agent, Fox):
                fox_counter += 1

                if not self._last_fox_ or self._last_fox_.food_eaten < agent.food_eaten:  # or self._last_fox_ not in self._agents_:
                    self._last_fox_ = agent
            elif isinstance(agent, Rabbit):
                rabbit_counter += 1

                if not self._last_rabbit_ or self._last_rabbit_.food_eaten < agent.food_eaten:
                    self._last_rabbit_ = agent

        if rabbit_counter < self._rabbits_number_ // 10:
            self._foxes_number_ -= 25

            self.clear_world()
            self.fill_world()

            # self._rabbit_refills_ = 0
        elif fox_counter < self._foxes_number_ // 10:
            self._foxes_number_ += 25

            self.clear_world()
            self.fill_world()

            # self._fox_refills_ = 0

        if (rabbit_counter > self._rabbits_number_ * self._rabbit_refill_threshold_
                and self._epoch_ > self._rabbit_epochs_refill_threshold_):
            self.clear_world()
            self.fill_world()

            self._rabbit_refills_ += 1

            self._rabbit_refill_threshold_ *= 1.1
            self._rabbit_epochs_refill_threshold_ *= 1.5

            self._epoch_ = ((self._fox_refills_ + self._rabbit_refills_) * DECAY) // 2
        elif (fox_counter > self._foxes_number_ * self._fox_refill_threshold_
              and self._epoch_ > self._fox_epochs_refill_threshold_):
            self.clear_world()
            self.fill_world()

            self._fox_refills_ += 1

            self._fox_refill_threshold_ *= 1.1
            self._fox_epochs_refill_threshold_ *= 1.5

            self._epoch_ = min(self._fox_epochs_refill_threshold_, self._rabbit_epochs_refill_threshold_) // 2

        self._counters_["food"].append(food_counter)
        self._counters_["fox"].append(fox_counter)
        self._counters_["rabbit"].append(rabbit_counter)

    def update_brains(self) -> None:
        for agent in self._agents_:
            if agent.brain:
                agent.brain.backward()

    def run(self) -> None:
        self.fill_world()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.fill_world()
                    if event.key == pygame.K_c:
                        self.clear_world()
                    if event.key == pygame.K_s:
                        self.draw_end()

            self.move_agents()
            self.check_dead()
            self.check_reproduce()
            self.count_agents()
            self.update_brains()
            self.draw_world()

            self._display_.blit(pygame.transform.scale(self._screen_, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))
            self._display_.blit(self._font_.render(f"Epoch: {self._epoch_}", True, (0, 0, 0)), (25, 25))
            self._clock_.tick(FPS)
            self._epoch_ += 1

            pygame.display.update()
