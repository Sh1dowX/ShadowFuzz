from mutator import mutate
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import random
import argparse
import hashlib
import time
import re
import json


#======================== Functions =========================

def normalize_output(text):
    text = text.strip()

    text = re.sub(
        r"\d{2,}",
        "<NUM>",
        text
    )
    return text
def run_target(target, input_file, timeout, coverage_output=None):
    if target.endswith(".py") and coverage_output is not None:
        command = [
            sys.executable,
            "coverage_runner.py",
            target,
            str(input_file),
            str(coverage_output)
        ]

        result = subprocess.run(
            command,
            timeout=timeout,
            capture_output=True,
            text=True
        )

        try:
            covered_lines = set(
                json.loads(Path(coverage_output).read_text())
            )
        except (FileNotFoundError, json.JSONDecodeError):
            covered_lines = set()

        return result, covered_lines

    if target.endswith(".py"):
        command = [
            sys.executable,
            target,
            str(input_file)
        ]
    else:
        command = [
            target,
            str(input_file)
        ]

    result = subprocess.run(
        command,
        timeout=timeout,
        capture_output=True,
        text=True
    )

    return result, set()
def save_crash(
        crash_directory,
        mutated_data,
        selected_seed,
        return_code,
        strategy,
        details,
        stderr,
        execution_time,
        original_size,
        mutated_size):

    crash_signature = calculate_crash_signature(return_code, stderr)
    signature_hash = calculate_hash(crash_signature.encode("utf-8"))
    short_hash = signature_hash[:12]

    size_difference = mutated_size - original_size
    timestamp = datetime.now().isoformat(timespec="seconds")

    crash_file = crash_directory / f"crashed_{short_hash}.bin"

    if crash_file.exists():
        return crash_file, False

    crash_file.write_bytes(mutated_data)

    crash_report = crash_directory / f"crashed_{short_hash}.txt"
    crash_report.write_text(
        f"File: {crash_file}\n"
        f"Timestamp: {timestamp}\n"
        f"----------\n"
        f"Original Seed: {selected_seed}\n"
        f"Original Size: {original_size} bytes\n"
        f"Mutated Size: {mutated_size} bytes\n"
        f"Size Difference: {size_difference} bytes\n"
        f"----------\n"
        f"Execution Time: {execution_time:.6f} seconds\n"
        f"Return Code: {return_code}\n"
        f"Crash Signature: {crash_signature}\n"
        f"----------\n"
        f"Strategy Used: {strategy}\n"
        f"Details:\n{details}\n"
        f"Target stderr:\n{stderr}\n",
        encoding="utf-8"
    )

    return crash_file, True
def save_to_corpus(corpus_directory, mutated_data, max_corpus):
    current_corpus_size = len(
        list(corpus_directory.glob("*.bin"))
    )

    if current_corpus_size >= max_corpus:
        return None, False

    file_hash = calculate_hash(mutated_data)
    short_hash = file_hash[:12]

    corpus_file = corpus_directory / f"corpus_{short_hash}.bin"

    if corpus_file.exists():
        return corpus_file, False

    corpus_file.write_bytes(mutated_data)

    return corpus_file, True
def corpus_contains(corpus_directory, data):
    file_hash = calculate_hash(data)
    short_hash = file_hash[:12]

    corpus_file = corpus_directory / f"corpus_{short_hash}.bin"

    return corpus_file.exists()
def save_hang(
        hang_directory,
        selected_seed,
        mutated_data,
        strategy,
        details,
        timeout,
        execution_time,
        original_size,
        mutated_size):
    file_hash = calculate_hash(mutated_data)
    short_hash = file_hash[:12]

    hang_file = hang_directory / f"hang_{short_hash}.bin"
    if hang_file.exists():
        return hang_file, False
    hang_file.write_bytes(mutated_data)

    timestamp = datetime.now().isoformat(timespec="seconds")
    size_difference = mutated_size - original_size

    hang_report = hang_directory / f"hang_{short_hash}.txt"
    hang_report.write_text(
        f"File: {hang_file}\n"
        f"Timestamp: {timestamp}\n"
        f"Original Seed: {selected_seed}\n"
        f"Original Size: {original_size} bytes\n"
        f"Mutated Size: {mutated_size} bytes\n"
        f"Size difference: {size_difference} bytes\n"
        f"Execution Time: {execution_time:.6f} seconds\n"
        f"Timeout: {timeout} seconds\n"
        f"Strategy Used: {strategy}\n"
        f"Details:\n{details}\n",
        encoding="utf-8"
    )

    return hang_file, True
def print_statistics(total_executions, crashed_count, duplicate_crash_count, hang_count, duplicate_hang_count, elapsed_time, successful_count, interesting_output_count, corpus_size):
    if total_executions != 0:
        crash_rate = crashed_count / total_executions * 100
        hang_rate = hang_count / total_executions * 100
    else:
        crash_rate = 0
        hang_rate = 0

    if elapsed_time > 0:
        executions_per_second = total_executions / elapsed_time
    else:
        executions_per_second = 0

    print("\n========== Statistics ==========")
    print(f"Total Executions: {total_executions}")
    print(f"Crashes Found: {crashed_count}")
    print(f"Duplicate Crashes: {duplicate_crash_count}")
    print(f"Hangs Found: {hang_count}")
    print(f"Duplicate Hangs: {duplicate_hang_count}")
    print(f"Crash Rate: {crash_rate:.2f}%")
    print(f"Hangs Rate: {hang_rate:.2f}%")

    print(f"\nElapsed Time: {elapsed_time:.2f} seconds")
    print(f"Executions Per Second: {executions_per_second:.2f}")

    print(f"\nSuccessful Executions: {successful_count}")

    print(f"\nInteresting Output: {interesting_output_count}")
    print(f"\nCorpus Size: {corpus_size}")
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument(
        "--iterations",
        type=int,
        default=5
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=2
    )
    parser.add_argument(
        "--stats-interval",
        type=int,
        default=100
    )
    parser.add_argument(
        "--replay",
        type=str,
        default=None,
        help="Replay a previously saved crash or hang file"
    )
    parser.add_argument(
        "--minimize",
        type=str,
        default=None,
        help="Minimize a previosly saved crash file"
    )
    parser.add_argument(
        "--max-corpus",
        type=int,
        default=1000
    )

    return parser.parse_args()
def load_seed_files(seed_directory):
    if not seed_directory.exists():
        raise FileNotFoundError(
            f"Seed directory not found: {seed_directory}"
        )

    seed_files = list(seed_directory.glob("*.bin"))

    if not seed_files:
        raise FileNotFoundError("No seed files found")

    return seed_files
def load_corpus_files(corpus_directory):
    if not corpus_directory.exists():
        return []

    return list(corpus_directory.glob("*.bin"))
def read_seed(selected_seed):
    with open(selected_seed, "rb") as f:
        original_data = f.read()

    return original_data
def create_directories(*directories):
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
def save_mutated_file(output_directory, mutated_data):
    new_file = output_directory / "current_input.bin"
    new_file.write_bytes(mutated_data)

    return new_file
def validate_arguments(args):
    if args.iterations <= 0:
        raise ValueError("Number of iterations must be greater than 0")
    if args.max_corpus <= 0:
        raise ValueError("Maximum corpus size must be greater than 0")
    if args.timeout <= 0:
        raise ValueError("Timeout must be greater than 0")
    target_file = Path(args.target)
    if args.stats_interval <= 0:
        raise ValueError("Statistics interval must be greater than 0")
    if args.replay is not None:
        replay_file = Path(args.replay)
        if not replay_file.exists():
            raise FileNotFoundError(
                f"Replay file not found: {replay_file}"
            )
    if args.minimize is not None:
        minimize_file = Path(args.minimize)
        if not minimize_file.exists():
            raise FileNotFoundError(
                f"Minimize file not found: {minimize_file}"
            )
        if not minimize_file.is_file():
            raise ValueError(
                "Minimize path must be a file"
            )
        if minimize_file.stat().st_size == 0:
            raise ValueError("Minimize file must not be empty")
        if args.replay is not None and args.minimize is not None:
            raise ValueError(
                "--replay and --minimize cannot be used together"
            )
    if not target_file.exists():
        raise FileNotFoundError(f"Target file not found: {target_file}")
def calculate_hash(data):
    file_hash = hashlib.sha256(data).hexdigest()
    return file_hash
def calculate_crash_signature(return_code, stderr):
    cleaned_stderr = stderr.strip()

    if cleaned_stderr:
        last_line = cleaned_stderr.splitlines()[-1]
    else:
        last_line = "no_stderr"

    signature = f"{return_code}|{last_line}"

    return signature
def replay_mode(target, replay_file, timeout):
    replay_path = Path(replay_file)

    print("========== Replay Mode ==========")
    print(f"Input File: {replay_path}")
    print(f"Target: {target}")

    execution_start = time.perf_counter()

    try:
        result, _covered_lines = run_target(
            target,
            replay_path,
            timeout
        )

        execution_time = time.perf_counter() - execution_start

    except subprocess.TimeoutExpired:
        execution_time = time.perf_counter() - execution_start

        print(f"Execution Time: {execution_time:.6f} seconds")
        print(f"Result: Hang reproduced")
        return

    print(f"Execution Time: {execution_time:.6f} seconds")
    print(f"Return Code: {result.returncode}")

    if result.stderr:
        print("\nTarget stderr:")
        print(result.stderr)

    if result.returncode != 0:
        crash_signature = calculate_crash_signature(
            result.returncode,
            result.stderr
        )

        print(f"Crash Signature: {crash_signature}")
        print("\nResult: Crash reproduced")
    else:
        print("\nResult: Crash was not reproduced")
def minimize_mode(target, crash_file, timeout):
    crash_path = Path(crash_file)

    original_data = crash_path.read_bytes()

    try:
        result, _covered_lines = run_target(
            target,
            crash_path,
            timeout
        )

    except subprocess.TimeoutExpired:
        print("This file causes a hang, not a crash")
        return

    if result.returncode == 0:
        print("The provided file does not reproduce a crash")
        return

    original_signature = calculate_crash_signature(
        result.returncode,
        result.stderr
    )

    print("========== Minimize Mode ==========")
    print(f"Crash file: {crash_path}")
    print(f"Original size: {len(original_data)}")
    print(f"Crash signature: {original_signature}")

    current_data = original_data
    index = 0

    while index < len(current_data):
        minimized_data = remove_byte(
            target,
            current_data,
            timeout,
            index,
            original_signature
        )

        if minimized_data is not None:
            current_data = minimized_data
            print(
                f"Removed byte at index {index}, "
                f"new size: {len(current_data)}"
            )
        else:
            index += 1

    output_file = crash_path.with_name(
        crash_path.stem + "_minimized.bin"
    )

    output_file.write_bytes(current_data)

    print("\n========== Minimization Complete ==========")
    print(f"Original size: {len(original_data)}")
    print(f"Minimized size: {len(current_data)}")
    print(f"Bytes removed: {len(original_data) - len(current_data)}")
    print(f"Saved to: {output_file}")
def remove_byte(
        target,
        current_data,
        timeout,
        index,
        original_signature):

    modified_data = bytearray(current_data)

    if index < 0 or index >= len(modified_data):
        return None

    del modified_data[index]

    temp_file = Path("temp_minimized.bin")
    temp_file.write_bytes(modified_data)

    try:
        result, _covered_lines = run_target(
            target,
            temp_file,
            timeout
        )

    except subprocess.TimeoutExpired:
        return None

    finally:
        temp_file.unlink(missing_ok=True)

    if result.returncode == 0:
        return None

    new_signature = calculate_crash_signature(
        result.returncode,
        result.stderr
    )

    if new_signature == original_signature:
        return bytes(modified_data)

    return None
def calculate_execution_signature(result):
    stdout = normalize_output(result.stdout)
    stderr = normalize_output(result.stderr)

    signature = (
        result.returncode,
        stdout,
        stderr
    )
    return signature
def prune_corpus(corpus_directory,input_files,input_energy,input_hits,productive_hits,max_corpus):

    corpus_files = list(corpus_directory.glob("*.bin"))

    if len(corpus_files) < max_corpus:
        return None

    candidates = [f for f in corpus_files if input_hits[f] > 0]

    if not candidates:
        # все corpus-файлы ещё непротестированы (hits == 0) - по efficiency
        # выбрать некого, но corpus всё равно полон и новый input иначе
        # никогда не сохранится. Fallback: удаляем по наименьшей energy,
        # как в старой версии prune_corpus.
        worst_file = None
        worst_energy = None

        for file in corpus_files:
            energy = input_energy[file]

            if worst_energy is None or energy < worst_energy:
                worst_energy = energy
                worst_file = file

        if worst_file is not None:
            worst_file.unlink()
            input_files.remove(worst_file)

            del input_energy[worst_file]
            del input_hits[worst_file]
            del productive_hits[worst_file]

        return worst_file

    worst_file = None
    worst_efficiency = None

    for file in candidates:
        efficiency = productive_hits[file] / input_hits[file]

        if worst_efficiency is None or efficiency < worst_efficiency:
            worst_efficiency = efficiency
            worst_file = file
        elif efficiency == worst_efficiency and input_hits[file] > input_hits[worst_file]:
            worst_file = file  # при равной efficiency - у кого больше hits, тот бесполезнее

    if worst_file is not None:
        worst_file.unlink()
        input_files.remove(worst_file)

        del input_energy[worst_file]
        del input_hits[worst_file]
        del productive_hits[worst_file]

    return worst_file
def fuzz_iteration(
        input_files,
        output_directory,
        crash_directory,
        hang_directory,
        corpus_directory,
        interesting_outputs,
        input_energy,
        target,
        timeout,
        max_corpus,
        input_hits,
        productive_hits,
        known_coverage):   # Делает одну интерацию фаззинга

    weight = []

    for file in input_files:
        weight.append(input_energy[file])

    selected_seed = random.choices(
        input_files,
        weights=weight,
        k=1
    )[0]
    input_hits[selected_seed] += 1
    efficiency = (
        productive_hits[selected_seed]
        / input_hits[selected_seed]
        * 100
    )

    print(
        f"Selected: {selected_seed.name} | "
        f"Energy: {input_energy[selected_seed]} | "
        f"Hits: {input_hits[selected_seed]} | "
        f"Productive: {productive_hits[selected_seed]} | "
        f"Efficiency: {efficiency:.2f}%"
    )

    original_data = read_seed(selected_seed)

    if selected_seed.parent.name == "seeds":  # Выводит то куда был сохранен новый интересный файл
        print(f"Selected seed: {selected_seed.parent.name}")
        print(f"File: {selected_seed.name}")

    second_seed_data = None

    if len(input_files) > 1:
        second_seed = random.choice(input_files)

        while second_seed == selected_seed:
            second_seed = random.choice(input_files)

        second_seed_data = read_seed(second_seed)

    mutated_data, strategy, details, mutation_stats = mutate(
        original_data,
        second_seed_data
    )
    original_size = len(original_data)
    mutated_size = len(mutated_data)

    new_file = save_mutated_file(
        output_directory,
        mutated_data
    )

    execution_start = time.perf_counter()
    coverage_output = output_directory / "coverage_tmp.json"
    coverage_output.unlink(missing_ok=True)  # защита от старого coverage, если прошлый запуск не успел его перезаписать

    try:
        result, covered_lines = run_target(
            target,
            new_file,
            timeout,
            coverage_output=coverage_output
        )
        execution_time = time.perf_counter() - execution_start

    except subprocess.TimeoutExpired:
        execution_time = time.perf_counter() - execution_start

        hang_file, is_new = save_hang(
            hang_directory,
            selected_seed,
            mutated_data,
            strategy,
            details,
            timeout,
            execution_time,
            original_size,
            mutated_size
        )

        if is_new:
            print(f"Hang Found: {hang_file}")
            productive_hits[selected_seed] += 1

            input_energy[selected_seed] = min(
                input_energy[selected_seed] + 2,
                10
            )

            prune_corpus(corpus_directory, input_files, input_energy, input_hits, productive_hits,
                         max_corpus)

            corpus_file, corpus_is_new = save_to_corpus(
                corpus_directory,
                mutated_data,
                max_corpus
            )
            if corpus_is_new:
                print(f"Saved to corpus: {corpus_file}")
                input_files.append(corpus_file)
                input_energy[corpus_file] = 1
                input_hits[corpus_file] = 0
                productive_hits[corpus_file] = 0

            return "new_hang", mutation_stats

        return "duplicate_hang", mutation_stats

    # coverage учитываем сразу для любого завершившегося запуска (crash
    # или нормальный) - раньше coverage от crash-запуска терялся, потому
    # что crash-ветка делала return до расчёта new_lines.
    new_lines = covered_lines - known_coverage
    if new_lines:
        known_coverage.update(new_lines)
        print(f"New coverage: +{len(new_lines)} lines (total {len(known_coverage)})")

    if result.returncode != 0:

        crash_file, is_new = save_crash(
            crash_directory,
            mutated_data,
            selected_seed,
            result.returncode,
            strategy,
            details,
            result.stderr,
            execution_time,
            original_size,
            mutated_size
        )

        if is_new:
            print(f"Crash Found: {crash_file}")
            productive_hits[selected_seed] += 1

            input_energy[selected_seed] = min(
                input_energy[selected_seed] + 2,
                10
            )

            prune_corpus(corpus_directory, input_files, input_energy, input_hits, productive_hits, max_corpus)

            corpus_file, corpus_is_new = save_to_corpus(
                corpus_directory,
                mutated_data,
                max_corpus
            )
            if corpus_is_new:
                print(f"Saved to corpus: {corpus_file}")
                input_files.append(corpus_file)
                input_energy[corpus_file] = 1
                input_hits[corpus_file] = 0
                productive_hits[corpus_file] = 0

            return "new_crash", mutation_stats

        return "duplicate_crash", mutation_stats

    execution_signature = calculate_execution_signature(result)

    is_new_signature = execution_signature not in interesting_outputs
    is_new_coverage = len(new_lines) > 0

    if is_new_signature or is_new_coverage:
        if is_new_signature:
            interesting_outputs.add(execution_signature)
        # known_coverage уже обновлён выше (сразу после run_target), здесь
        # используем is_new_coverage только как флаг "интересности"

        productive_hits[selected_seed] += 1

        input_energy[selected_seed] = min(
            input_energy[selected_seed] + 1, # Увеличивает energy выбранного seed на 1
            10 # Не дает energy стать больше 10
        )

        prune_corpus(corpus_directory, input_files, input_energy, input_hits, productive_hits, max_corpus)

        corpus_file, corpus_is_new = save_to_corpus(
            corpus_directory,
            mutated_data,
            max_corpus
        )

        if corpus_is_new:
            print(f"Interesting Input saved: {corpus_file}")
            input_files.append(corpus_file)
            input_energy[corpus_file] = 1
            input_hits[corpus_file] = 0
            productive_hits[corpus_file] = 0
    else:
        input_energy[selected_seed] = max(
            input_energy[selected_seed] - 1,
            1
        )


    return "ok", mutation_stats

# ========================= Main Function =========================

def main():
    seed_directory = Path("seeds")
    output_directory = Path("outputs")
    crash_directory = Path("crashes")
    hang_directory = Path("hangs")
    corpus_directory = Path("corpus")

    args = parse_arguments()
    validate_arguments(args)
    interesting_output = set()
    known_coverage = set()

    if args.replay is not None:
        replay_mode(
            args.target,
            args.replay,
            args.timeout
        )
        return
    if args.minimize is not None:
        minimize_mode(
            args.target,
            args.minimize,
            args.timeout
        )
        return

    seed_files = load_seed_files(seed_directory)
    corpus_files = load_corpus_files(corpus_directory)

    input_files = seed_files + corpus_files

    input_energy = {}
    input_hits = {}
    productive_hits = {}

    for file in input_files:
        input_energy[file] = 1
        input_hits[file] = 0
        productive_hits[file] = 0

    create_directories(
        output_directory,
        crash_directory,
        hang_directory,
        corpus_directory,
    )

    total_executions = 0
    crashed_count = 0
    hang_count = 0
    duplicate_crash_count = 0
    duplicate_hang_count = 0
    successful_count = 0
    interesting_output_count = 0
    corpus_size = len(corpus_files)

    total_mutation_stats = {
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

    start_time = time.perf_counter()

    try:
        for i in range(args.iterations):
            status, iteration_mutation_stats = fuzz_iteration(
                input_files,
                output_directory,
                crash_directory,
                hang_directory,
                corpus_directory,
                interesting_output,
                input_energy,
                args.target,
                args.timeout,
                args.max_corpus,
                input_hits,
                productive_hits,
                known_coverage
            )

            for name, count in iteration_mutation_stats.items():
                total_mutation_stats[name] += count

            total_executions += 1

            if status == "new_crash":
                crashed_count += 1
            elif status == "duplicate_crash":
                duplicate_crash_count += 1
            elif status == "new_hang":
                hang_count += 1
            elif status == "duplicate_hang":
                duplicate_hang_count += 1

            elif status == "ok":
                successful_count += 1

            interesting_output_count = len(interesting_output)
            corpus_size = len(input_files) - len(seed_files)

            if total_executions % args.stats_interval == 0:
                elapsed_time = time.perf_counter() - start_time
                print_statistics(
                    total_executions,
                    crashed_count,
                    duplicate_crash_count,
                    hang_count,
                    duplicate_hang_count,
                    elapsed_time,
                    successful_count,
                    interesting_output_count,
                    corpus_size
                )
                print("==================================")

    except KeyboardInterrupt:
        print("\nFuzzing stopped by user")

    elapsed_time = time.perf_counter() - start_time

    print_statistics(
        total_executions,
        crashed_count,
        duplicate_crash_count,
        hang_count,
        duplicate_hang_count,
        elapsed_time,
        successful_count,
        interesting_output_count,
        corpus_size
    )
    print("\n============= Mutation Statistics ==============")

    for name, count in total_mutation_stats.items():
        print(f"{name}: {count}")

if __name__ == "__main__":
    main()