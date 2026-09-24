# ShadowFuzz

ShadowFuzz is an educational feedback-guided fuzzer written in Python. It mutates binary input files, executes a target program, and uses execution feedback to discover crashes, hangs, and new execution behavior.

## Features

- 17 mutation strategies, including bit flipping, byte insertion and deletion, arithmetic mutations, and cross-seed block copying
- Weighted seed selection and adaptive input energy
- Python line-coverage feedback
- Output-based feedback
- Corpus management and pruning
- Crash and hang detection
- Crash deduplication
- Crash replay and minimization
- Execution and mutation statistics

## How It Works

1. Load initial seed files and previously saved corpus inputs.
2. Select an input using weighted random selection based on its energy.
3. Apply multiple randomly selected mutation strategies.
4. Execute the target program with the mutated input.
5. Collect execution results and, for Python targets, executed line numbers.
6. Identify crashes, hangs, new output signatures, and new coverage.
7. Save useful inputs and adjust seed energy based on productivity.
8. Repeat the process.

## Requirements

- Python 3
- No external Python packages required

## Getting Started

Clone the repository:

```bash
git clone https://github.com/Sh1dowX/ShadowFuzz.git
cd ShadowFuzz
```

Place at least one binary seed file in the `seeds/` directory.

Run ShadowFuzz:

```bash
python fuzz.py --target examples/test_target.py --iterations 10000 --timeout 2
```

The example command requires `examples/test_target.py` to be present. You can replace it with your own target program.

## Usage

```bash
python fuzz.py --target TARGET [--iterations N] [--timeout SECONDS] [--stats-interval N] [--max-corpus N]
```

Replay a saved crash:

```bash
python fuzz.py --target examples/test_target.py --replay crashes/CRASH_FILE.bin
```

Minimize a saved crash:

```bash
python fuzz.py --target examples/test_target.py --minimize crashes/CRASH_FILE.bin
```

## Mutation Engine

The mutation engine applies multiple weighted mutation strategies to each selected input. These include byte and bit mutations, block operations, interesting integer values, file shrinking and expansion, and copying blocks from another seed.

Mutation weights control which strategies are selected. Input energy independently controls how likely a seed is to be selected.

## Coverage and Feedback

For Python targets, ShadowFuzz uses `coverage_runner.py` and `sys.settrace()` to record executed lines.

The fuzzer compares the lines reached by each input against its known coverage. Inputs reaching previously unseen lines can be retained for future mutations.

ShadowFuzz also tracks output signatures to identify changes in execution behavior.

## Corpus Management

The corpus stores interesting inputs that can be reused as future mutation sources.

ShadowFuzz tracks selection counts, productive selections, and input energy. When the corpus reaches its configured size limit, pruning makes room for new inputs based on productivity and fallback criteria.

## Crash and Hang Detection

ShadowFuzz treats non-zero process exit codes as crashes and executions exceeding the configured timeout as hangs.

Crash signatures are generated from the exit code and the final line of standard error. Matching signatures are treated as duplicate crashes.

Saved crashes can be replayed and minimized.

## Output Directories

| Directory | Purpose |
| --- | --- |
| `seeds/` | Initial input files |
| `corpus/` | Interesting inputs retained for future mutations |
| `crashes/` | Unique crashing inputs and reports |
| `hangs/` | Inputs that exceed the timeout |
| `outputs/` | Temporary execution files |

## Limitations

- Coverage instrumentation currently supports Python targets only.
- Coverage is line-based rather than edge-based.
- Native executables can be tested without coverage instrumentation.
- Fuzzing is single-process.
- Coverage state is not persisted between sessions.
- Non-zero exit codes may also represent ordinary program errors, not necessarily security vulnerabilities.

## Roadmap

- Native binary coverage instrumentation
- Edge coverage
- Persistent coverage state
- Parallel fuzzing
- Improved crash minimization

## Responsible Use

Only test software that you own or are authorized to assess.

## License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
