import numpy
import torch
import torch.nn as nn

from source.constants import MOVES, DECAY, SCAN_DIAMETER


class Brain(nn.Module):
    WEIGHTS_LENGTH = 8
    MUTATION_FACTOR = 4

    def __init__(self, state_dict: dict = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._input_shape_ = SCAN_DIAMETER ** 2

        self._flatten_ = nn.Flatten()
        self._softmax_ = nn.Softmax(dim=1)

        self._model_ = nn.Sequential(
            nn.Linear(self._input_shape_, self.WEIGHTS_LENGTH),
            nn.ReLU(),
            nn.Linear(self.WEIGHTS_LENGTH, self.WEIGHTS_LENGTH),
            nn.ReLU(),
            nn.Linear(self.WEIGHTS_LENGTH, len(MOVES))
        )

        self._probabilities_ = None
        self._reward_ = torch.tensor(0.0)

        if state_dict:
            self._model_.load_state_dict(state_dict)

    def forward(self, input_data: numpy.ndarray) -> int:
        output = self._model_(torch.tensor(numpy.expand_dims(input_data, axis=0)))
        self._probabilities_ = self._softmax_(output).argmax(1)

        return self._probabilities_.numpy()

    def calculate_reward(self, scan: list[int]) -> None:
        if self._probabilities_ is None:
            return

        priorities = [torch.exp(torch.tensor(-(len(scan) - index))) for index in range(1, len(scan) + 1)]

        for scanned, priority in zip(scan, priorities):
            self._reward_ += torch.sum(self._probabilities_ * torch.tensor(scanned) * priority)

    def reward_once(self) -> None:
        self._reward_ += torch.sum(self._probabilities_ * 5.0)

    def backward(self) -> None:
        with torch.no_grad():
            for parameter in self.parameters():
                if parameter.grad is not None:
                    parameter += 1e-3 * parameter.grad

    def mutate(self, epoch: int) -> None:
        if epoch > DECAY * 6:
            return

        with torch.no_grad():
            for parameter in self.parameters():
                if numpy.random.rand() < 0.5 / numpy.exp(epoch / DECAY):
                    parameter.copy_(torch.randn_like(parameter))
