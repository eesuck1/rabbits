from source.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCAN_DIAMETER

import numpy

temp_mask = numpy.zeros((SCAN_DIAMETER // 2, SCAN_DIAMETER, SCAN_DIAMETER), dtype=numpy.bool)

for i in range(SCAN_DIAMETER // 2):
    temp_mask[i, i, i:SCAN_DIAMETER - i] = 1
    temp_mask[i, i:SCAN_DIAMETER - 1 - i, SCAN_DIAMETER - 1 - i] = 1
    temp_mask[i, i:SCAN_DIAMETER - i, i] = 1
    temp_mask[i, SCAN_DIAMETER - 1 - i, i:SCAN_DIAMETER - i] = 1

SCAN_MASKS = numpy.zeros((SCAN_DIAMETER // 2, SCAN_DIAMETER ** 2), dtype=numpy.bool)

for i in range(SCAN_DIAMETER // 2):
    SCAN_MASKS[i] = temp_mask[i].flatten()


def get_random_coordinate() -> tuple[float, float]:
    return (numpy.random.randn() + 2) / 4 * (SCREEN_WIDTH - 1), (numpy.random.randn() + 2) / 4 * (SCREEN_HEIGHT - 1)
