import random

# ========== Mutations ===========
def mutate_bytes(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return bytes(mutated), "File was empty"

    changes = []
    mutation_amount = random.randint(1, min(10, len(mutated)))

    for _ in range(mutation_amount):
        position = random.randrange(len(mutated))
        old_value = mutated[position]
        new_value = random.randint(0, 255)

        mutated[position] = new_value

        changes.append(
            f"Position: {position}, "
            f"Old value: {old_value}, "
            f"New value: {new_value}"
        )

    details = "\n".join(changes)

    return bytes(mutated), details
def insert_random_byte(data):
    mutated = bytearray(data)

    position = random.randrange(len(mutated) + 1)
    new_value = random.randint(0, 255)

    mutated.insert(position, new_value)  # Вставляет в mutated новый байт

    details = (
        f"Position: {position}\n"
        f"Inserted Value: {new_value}"
    )

    return bytes(mutated), details
def delete_random_byte(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return bytes(mutated), "File was empty"

    position = random.randrange(len(mutated))
    deleted_value = mutated[position]

    del mutated[position]

    details = (
        f"Position: {position}\n"
        f"Deleted value: {deleted_value}"
    )

    return bytes(mutated), details
def flip_random_bit(data):
    mutated = bytearray(data)
    if len(mutated) == 0:
        return bytes(mutated), "File was empty"

    position = random.randrange(len(mutated))
    bit_position = random.randint(0, 7)

    old_value = mutated[position]
    mutated[position] ^= (1 << bit_position)   # 00000001 -> 000010000 move left ( bit positions )
    new_value = mutated[position]

    details = (
        f"Position: {position}\n"
        f"Bit position: {bit_position}\n"
        f"Old value: {old_value}\n"
        f"New value: {new_value}"
    )

    return bytes(mutated), details
def magic_value(data):
    MAGIC_VALUE = [
        b"\x00",
        b"\xff",
        b"\x7f",
        b"\x80",
        b"AAAA",
        b"ABCD",
        b"\xff\x00\xff"
    ]

    mutated = bytearray(data)

    magic = random.choice(MAGIC_VALUE)

    position = random.randrange(len(mutated) + 1)
    mutated[position: position] = magic

    details = (
        f"Position: {position}\n"
        f"Magic Value: {magic}\n"
    )

    return bytes(mutated), details
def duplicate_block(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return bytes(mutated), "File was empty"

    start_position = random.randrange(len(mutated))

    available_length = len(mutated) - start_position
    max_block_length = min(available_length, 64)   # Ограничиваем размер input

    block_length = random.randint(1, max_block_length)

    block = mutated[
        start_position:start_position + block_length
    ]

    insert_position = random.randrange(len(mutated) + 1)
    mutated[insert_position:insert_position] = block

    details = (
        f"Source position: {start_position}\n"
        f"Block length: {block_length}\n"
        f"Insert position: {insert_position}"
    )

    return bytes(mutated), details
def overwrite_block(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return bytes(mutated), "File was empty"

    start_position = random.randrange(len(mutated))         #  Ищем начало
    available_length = len(mutated) - start_position        #
    max_block_length = min(available_length, 64)            #  Ищем разрешенный максимум для блока
    block_length = random.randint(1, max_block_length)   #  Ищем длину
    #
    block = mutated[start_position:start_position + block_length]  # создаем Block который мы копируем

    new_bytes = random.randbytes(block_length)

    mutated[start_position:start_position + block_length] = new_bytes

    details = (
        f"Start position: {start_position}\n"
        f"Original block: {block}\n"
        f"Block length: {block_length}\n"
        f"Random bytes: {new_bytes}\n"
    )

    return bytes(mutated), details
def swap_block(data):
    mutated = bytearray(data)

    if len(mutated) < 2:
        return bytes(mutated), "File too small to swap"

    max_block_length = min(len(mutated) // 2, 64)
    block_length = random.randint(1, max_block_length)

    start_1 = random.randrange(0, len(mutated) - block_length * 2 + 1)

    start_2 = random.randrange(start_1 + block_length, len(mutated) - block_length + 1)
    #
    block_1 = mutated[start_1:start_1 + block_length]
    block_2 = mutated[start_2:start_2 + block_length]

    mutated[start_1:start_1 + block_length] = block_2
    mutated[start_2:start_2 + block_length] = block_1

    details = (
        f"First start position: {start_1}\n"
        f"Second start position: {start_2}\n"
        f"Block length: {block_length}\n"
        f"First block: {block_1}\n"
        f"Second block: {block_2}\n"
    )

    return bytes(mutated), details
def reverse_block(data):
    mutated = bytearray(data)

    if len(mutated) < 2:
        return bytes(mutated), "File too small to reverse"

    max_block_length = min(len(mutated), 64)
    block_length = random.randint(2, max_block_length)

    start_position = random.randrange(
        len(mutated) - block_length + 1)
    #
    block = mutated[start_position:start_position + block_length]  # создаем Block который мы копируем

    reversed_block = bytes(reversed(block)) # Так как reversed(bytes) не возвращает bytes, а ввозвращает объект-итератор лучше сначало перевернуть блок

    mutated[start_position:start_position + block_length] = reversed_block

    details = (
        f"Start position: {start_position}\n"
        f"Block length: {block_length}\n"
        f"Original block: {block}\n"
        f"Reversed block: {reversed_block}"
    )

    return bytes(mutated), details
def set_block_value(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return  bytes(mutated), "File was empty"

    start_position = random.randrange(len(mutated))  #
    available_length = len(mutated) - start_position  #
    max_block_length = min(available_length, 64)  #
    block_length = random.randint(1, max_block_length)  #
    #
    block = mutated[start_position:start_position + block_length]  # создаем Block который мы копируем

    random_byte = random.randbytes(1)
    random_byte = block_length * random_byte

    mutated[start_position:start_position + block_length] = random_byte

    details = (
        f"Start position: {start_position}\n"
        f"Original block: {block}\n"
        f"Block length: {block_length}\n"
        f"Repeated byte: {random_byte}\n"
    )

    return bytes(mutated), details
def arithmetic_mutation(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return bytes(mutated), "File was empty"

    position = random.randint(0, len(mutated) - 1)
    random_number = random.randint(1, 16)

    random_choose = random.randint(0, 1)
    old_value = mutated[position]

    if random_choose == 1:
        new_value = (old_value + random_number) % 256
        operation = f"+{random_number}"
    else:
        new_value = (old_value - random_number) % 256
        operation = f"-{random_number}"
    mutated[position] = new_value

    details = (
        f"Position: {position}\n"
        f"Old Value: {old_value}\n"
        f"Operation: {operation}\n"
        f"New Value: {new_value}"
    )

    return bytes(mutated), details
def interesting_integer(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return bytes(mutated), "File was empty"

    position = random.randint(0, len(mutated) - 1)
    old_value = mutated[position]
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

    mutated[position] = random_byte

    details = (
        f"Position: {position}\n"
        f"Old Value: {old_value}\n"
        f"Interesting Value: {random_byte}\n"
        f"New Value: {mutated[position]}"
    )
    return bytes(mutated), details
def shrink_file(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return bytes(mutated), "File was empty"

    start_position = random.randrange(len(mutated))
    available_length = len(mutated) - start_position
    max_block_length = min(available_length, 64)  # Ограничиваем размер input
    block_length = random.randint(1, max_block_length)
    block = mutated[
        start_position:start_position + block_length
    ]

    del mutated[start_position:start_position + block_length]

    details = (
        f"Start position: {start_position}\n"
        f"Block length: {block_length}\n"
        f"Original block: {block}\n"
        f"Original size: {len(data)}\n"
        f"New size: {len(mutated)}"
    )

    return bytes(mutated), details
def expand_file(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return bytes(mutated), "File was empty"

    original_size = len(mutated)
    position = random.randrange(len(mutated))
    random_length = random.randint(1, 64)
    random_bytes = random.randbytes(random_length)

    mutated[position:position] = random_bytes

    details = (
        f"Position: {position}\n"
        f"Inserted bytes: {random_bytes}\n"
        f"Original size: {original_size}\n"
        f"New size: {len(mutated)}"

    )
    return bytes(mutated), details
def xor_block(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return bytes(mutated), "File was empty"

    start_position = random.randrange(len(mutated))
    available_length = len(mutated) - start_position
    max_block_length = min(available_length, 64)
    block_length = random.randint(1, max_block_length)

    xor_value = random.randint(0, 255)

    block = mutated[start_position:start_position + block_length]

    for i in range(start_position, start_position + block_length):
        mutated[i] ^= xor_value

    new_block = mutated[start_position:start_position + block_length]
    details = (
        f"Start position: {start_position}\n"
        f"Block length: {block_length}\n"
        f"Original block: {block}\n"
        f"New block: {new_block}"
    )
    return bytes(mutated), details
def insert_repeated_bytes(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return bytes(mutated), "File was empty"

    original_size = len(mutated)

    position = random.randrange(len(mutated) + 1)
    repeated_byte = random.randbytes(1)
    repeat_count = random.randint(2, 32)
    pattern = repeated_byte * repeat_count

    mutated[position:position] = pattern

    new_block = mutated[position:position + repeat_count]

    details = (
        f"Position: {position}\n"
        f"Repeated byte: {repeated_byte}\n"
        f"Repeated count: {repeat_count}\n"
        f"Pattern: {pattern}\n"
        f"New block: {new_block}"
        f"Original size: {original_size}"
        f"New size: {len(mutated)}"
    )
    return bytes(mutated), details
def copy_block_from_seed(data, second_seed_data):
    mutated = bytearray(data)
    second_data = bytearray(second_seed_data)

    if len(second_data) == 0:
        return bytes(mutated), "Second seed was empty"

    source_position = random.randrange(len(second_data))

    available_length = len(second_data) - source_position
    max_block_length = min(available_length, 64)
    block_length = random.randint(1, max_block_length)

    block = second_data[source_position:source_position + block_length]
    insert_position = random.randrange(len(mutated) + 1)

    mutated[insert_position:insert_position] = block

    details = (
        f"Source position: {source_position}\n"
        f"Inserted position: {insert_position}\n"
        f"Block length: {block_length}\n"
        f"Original size: {len(data)}\n"
        f"New size: {len(mutated)}"
    )
    return bytes(mutated), details
# ===========


def mutate(data, second_seed_data=None):
    mutated_data = data

    strategies = []
    all_details = []

    mutation_count = random.randint(2, 6)

    mutation = [
        "mutate_bytes",
        "insert_random_byte",
        "delete_random_byte",
        "flip_random_bit",
        "magic_value",
        "duplicate_block",
        "overwrite_block",
        "swap_block",
        "reverse_block",
        "set_block_value",
        "arithmetic_mutation",
        "interesting_integer",
        "shrink_file",
        "expand_file",
        "xor_block",
        "insert_repeated_byte",
    ]
    weights = [
        10,
        5,
        5,
        15,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        5,

    ]

    if second_seed_data is not None:
        mutation.append("copy_block_from_seed")
        weights.append(5)

    mutation_stats = {
        "mutate_bytes": 0,
        "insert_random_byte": 0,
        "delete_random_byte": 0,
        "flip_random_bit": 0,
        "magic_value": 0,
        "duplicate_block": 0,
        "overwrite_block": 0,
        "swap_block": 0,
        "reverse_block": 0,
        "set_block_value": 0,
        "arithmetic_mutation": 0,
        "interesting_integer": 0,
        "shrink_file": 0,
        "expand_file": 0,
        "xor_block": 0,
        "insert_repeated_byte": 0,
        "copy_block_from_seed": 0,
    }

    for index in range(mutation_count):
        choice = random.choices(
            mutation,
            weights=weights,
            k=1 # Скок элементов ( мутации ) выбрет функция
        )[0] # <- на выходе функция нам дает список. [0] - делает из списка строку

        mutation_stats[choice] += 1

        if choice == "mutate_bytes":
            mutated_data, details = mutate_bytes(mutated_data)
            strategy = "mutate_bytes"
        elif choice == "insert_random_byte":
            mutated_data, details = insert_random_byte(mutated_data)
            strategy = "insert_random_byte"
        elif choice == "flip_random_bit":
            mutated_data, details = flip_random_bit(mutated_data)
            strategy = "flip_random_bit"
        elif choice == "delete_random_byte":
            mutated_data, details = delete_random_byte(mutated_data)
            strategy = "delete_random_byte"
        elif choice == "magic_value":
            mutated_data, details = magic_value(mutated_data)
            strategy = "magic_value"
        elif choice == "duplicate_block":
            mutated_data, details = duplicate_block(mutated_data)
            strategy = "duplicate_block"
        elif choice == "overwrite_block":
            mutated_data, details = overwrite_block(mutated_data)
            strategy = "overwrite_block"
        elif choice == "swap_block":
            mutated_data, details = swap_block(mutated_data)
            strategy = "swap_block"
        elif choice == "reverse_block":
            mutated_data, details = reverse_block(mutated_data)
            strategy = "reverse_block"
        elif choice == "set_block_value":
            mutated_data, details = set_block_value(mutated_data)
            strategy = "set_block_value"
        elif choice == "arithmetic_mutation":
            mutated_data, details = arithmetic_mutation(mutated_data)
            strategy = "arithmetic_mutation"
        elif choice == "interesting_integer":
            mutated_data, details = interesting_integer(mutated_data)
            strategy = "interesting_integer"
        elif choice == "shrink_file":
            mutated_data, details = shrink_file(mutated_data)
            strategy = "shrink_file"
        elif choice == "expand_file":
            mutated_data, details = expand_file(mutated_data)
            strategy = "expand_file"
        elif choice == "xor_block":
            mutated_data, details = xor_block(mutated_data)
            strategy = "xor_block"
        elif choice == "insert_repeated_byte":
            mutated_data, details = insert_repeated_bytes(mutated_data)
            strategy = "insert_repeated_byte"
        elif choice == "copy_block_from_seed":
            mutated_data, details = copy_block_from_seed(mutated_data, second_seed_data)
            strategy = "copy_block_from_seed"

        strategies.append(strategy)
        all_details.append(
            f"Mutation {index + 1}: {strategy}\n{details}"
        )

    strategy_text = " -> ".join(strategies)
    details_text = "\n\n".join(all_details)

    print("Mutation statistics:")
    for name, count in mutation_stats.items():
        print(f"{name}: {count}")

    return mutated_data, strategy_text, details_text, mutation_stats