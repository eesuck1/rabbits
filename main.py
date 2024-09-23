from source.simulation import Simulation


def main() -> None:
    simulation = Simulation(50, 15, 500)
    simulation.run()


if __name__ == '__main__':
    main()
