import random

def mutate_bytes(data):
    mutated = bytearray(data) # Создает копию файла для того чтобы не ломать оригинальный файл

    for _ in range(random.randint(5,10)):
        position = random.randrange(len(mutated)) # Выбирает случайную позицию ( например если есть слово Hello ( 72 101 108 108 111) Случайно выбирает букву )
        new_value = random.randint(0, 255) # Создает случайный байт

        mutated[position] = new_value  # Заменяет старый байт на новый
        print(f"{_}) Позиция: {position}, Новое занчение: {new_value}") # Выводим ( позицию и новое значение ) чтобы нам легче было понять что мы изменили

    return bytes(mutated) # Возращает mutated обратно в bytes

def insert_random_byte(data):
    mutated = bytearray(data)

    position = random.randrange(len(mutated))
    new_value = random.randint(0, 255)

    mutated.insert(position, new_value)  # Вставляет в mutated новый байт

    return bytes(mutated)

def mutate(data):

    choice = random.randint(0, 1)
    if choice == 0:
        print("Mutate_bytes choosen")
        return mutate_bytes(data)
    else:
        print("Insert_random_byte choosen")
        return insert_random_byte(data)