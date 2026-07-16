import random

def mutate_bytes(data):
    mutated = bytearray(data) # Создает копию файла для того чтобы не ломать оригинальный файл

    if len(mutated) == 0:
        return bytes(mutated)

    for _ in range(random.randint(5,10)):
        position = random.randrange(len(mutated)) # Выбирает случайную позицию ( например если есть слово Hello ( 72 101 108 108 111) Случайно выбирает букву )
        new_value = random.randint(0, 255) # Создает случайный байт

        mutated[position] = new_value  # Заменяет старый байт на новый
        print(f"{_}) Позиция: {position}, Новое занчение: {new_value}") # Выводим ( позицию и новое значение ) чтобы нам легче было понять что мы изменили

    return bytes(mutated) # Возращает mutated обратно в bytes


def insert_random_byte(data):
    mutated = bytearray(data)

    if len(mutated) == 0:
        return bytes(mutated)

    position = random.randrange(len(mutated))
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
        return bytes(mutated)
    position = random.randrange(len(mutated))
    del mutated[position]

    return bytes(mutated)


def flip_random_bit(data):
    mutated = bytearray(data)
    if len(mutated) == 0:
        return bytes(mutated)

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


def mutate(data):
    choice = random.randint(0, 3)

    if choice == 0:
        print("mutate_bytes chosen")
        mutated_data = mutate_bytes(data)
        return mutated_data, "mutate_bytes", "Multiple bytes replaced"

    elif choice == 1:
        print("insert_random_byte chosen")
        mutated_data, details = insert_random_byte(data)
        return mutated_data, "insert_random_byte", details

    elif choice == 2:
        print("flip_random_bit chosen")
        mutated_data, details = flip_random_bit(data)
        return mutated_data, "flip_random_bit", details

    else:
        print("delete_random_byte chosen")
        mutated_data = delete_random_byte(data)
        return mutated_data, "delete_random_byte", "One byte deleted"
