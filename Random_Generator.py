import random


def RandomGenerator(filename, count, seed=None):
    # Set the seed for random number generation
    if seed is not None:
        random.seed(seed)

    # Set the seed for random number generation
    if seed is not None:
        random.seed(seed)

    # Create and open the file in write mode
    with open(filename, 'w') as file:
        for _ in range(count):
            random_number = random.random()
            file.write(f"{random_number}\n")


filename = "random_numbers.txt"
seed = 42
count = 2**20
RandomGenerator(filename, count,seed)
print(f"{count} Random number with seed {seed} has been exported")





