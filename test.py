import random
interesting_value = [
    0,
    1,
    2,
    7,
    15,
    16,
    31,
    32,
    63,
    64,
    127,
    128,
    254,
    255
]

random_byte = random.choice(interesting_value)

print(random_byte)