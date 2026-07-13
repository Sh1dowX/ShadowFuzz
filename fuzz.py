from mutator import mutate_bytes
from pathlib import Path

original_file = Path("seeds/seeds.bin")
output_directory = Path("outputs")

if not original_file.exists():
    raise FileNotFoundError(f"Original file not found: {original_file}")

with open(original_file, "rb") as f:

    output_directory.parent.mkdir(parents=True, exist_ok=True)

    original_data = f.read()

    for i in range(5):
        mutated_data = mutate_bytes(original_data) # Получаем измененный текст с неправильными bytes

        new_file = Path(f"{output_directory}/mutated_{i}.bin")

        new_file.write_bytes(mutated_data)

# ================ Выводим ================
print(original_data) # Оригинал
print(f"Mutated text saved in: {output_directory}") # Измененный текст