from mutator import mutate
from pathlib import Path
import subprocess
import sys
import random


seed_directory = Path("seeds")
output_directory = Path("outputs")
crash_directory = Path("crashes")
hang_directory = Path("hangs")


if not seed_directory.exists():
    raise FileNotFoundError(
        f"Seed directory not found: {seed_directory}"
    )

seed_files = list(seed_directory.glob("*.bin"))

if not seed_files:
    raise FileNotFoundError("No seed files found")


output_directory.mkdir(parents=True, exist_ok=True)
crash_directory.mkdir(parents=True, exist_ok=True)
hang_directory.mkdir(parents=True, exist_ok=True)

total_executions = 0
crashed_count = 0
hang_count = 0


for i in range(5):
    selected_seed = random.choice(seed_files)

    with open(selected_seed, "rb") as f:
        original_data = f.read()

    print(f"Selected seed: {selected_seed}")

    mutated_data, strategy, details = mutate(original_data)

    new_file = output_directory / f"mutated_{i}.bin"
    new_file.write_bytes(mutated_data)
    
    try:
        result = subprocess.run([
            sys.executable,
            "target.py",
            str(new_file)

        ],
        timeout=2 # У Target будет ток 2 секунды чтобы выполнитсья
    )
    except subprocess.TimeoutExpired:
        hang_file = hang_directory / f"hang_{i}.bin"
        hang_file.write_bytes(mutated_data)

        print(f"Hang found: {new_file}")

        hang_count += 1
        total_executions += 1
        continue

    total_executions += 1

    if result.returncode != 0:
        crash_file = crash_directory / f"crashed_{i}.bin"
        crash_file.write_bytes(mutated_data)

        crash_report = crash_directory / f"crashed_{i}.txt"
        crash_report.write_text(
            f"File: {crash_file}\n"
            f"Original Seed: {selected_seed}\n"
            f"Return Code: {result.returncode}\n"
            f"Strategy Used: {strategy}\n"
            f"Details:\n{details}\n",
            encoding="utf-8"
        )

        print(f"Crash Found: {crash_file}")
        crashed_count += 1

    print(f"File: {new_file}")
    print(f"Return Code: {result.returncode}")
    print()


crash_rate = crashed_count / total_executions * 100

print("========== Statistics ==========")
print(f"Total Executions: {total_executions}")
print(f"Crashes Found: {crashed_count}")
print(f"Crash Rate: {crash_rate:.2f}%")