from mutator import mutate
from pathlib import Path
import subprocess
import sys

original_file = Path("seeds/seeds.bin")
output_directory = Path("outputs")
crash_directory = Path("crashes")

if not original_file.exists():
    raise FileNotFoundError(f"Original file not found: {original_file}")

with open(original_file, "rb") as f:

    output_directory.mkdir(parents=True, exist_ok=True)
    crash_directory.mkdir(parents=True, exist_ok=True)

    original_data = f.read()

    total_executions = 0
    crashed_count = 0

    for i in range(5):
        mutated_data = mutate(original_data) # Получаем измененный текст с неправильными bytes

        new_file = Path(f"{output_directory}/mutated_{i}.bin")  # Каждый раз создаёт новый output  файл

        new_file.write_bytes(mutated_data)

        result = subprocess.run([
            sys.executable,
            "target.py",
            str(new_file)
        ])

        if result.returncode != 0:
            crash_file = Path(f"{crash_directory}/crashed_{i}.bin")
            crash_file.write_bytes(mutated_data)
            crash_file_txt = Path(f"{crash_directory}/crashed_{i}.txt")
            crash_file_txt.write_text(
                f"File: {crash_file}\n"
                f"Return Code: {result.returncode}\n"
            )
            print("Crash Found !")
            crashed_count += 1

        print("File: ", new_file)  # Путь output файла
        print("Return Code: ",result.returncode)  # Показывает завершился ли код ( 0 - завершился нормально, 1 - завершился с ошибкой )


        total_executions += 1
# ================ Выводим ================

print(f"Total Executions: {total_executions}")
print(f"Crashes Found: {crashed_count}")
crash_rate = crashed_count / total_executions * 100
print(f"Crash Rate: {crash_rate:.2f}%")