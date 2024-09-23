import matplotlib.pyplot as plt
import numpy

from source.constants import DECAY


def draw() -> None:
    t = numpy.arange(3000)
    y = 0.5 / numpy.exp(t / DECAY)

    plt.plot(y)
    plt.grid()
    plt.show()


if __name__ == '__main__':
    draw()
