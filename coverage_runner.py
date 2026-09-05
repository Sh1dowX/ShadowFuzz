import sys
import runpy
import json
import traceback
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: coverage_runner.py <target_script> <input_file> [coverage_output_file]",
            file=sys.stderr
        )
        sys.exit(2)

    target_script = sys.argv[1]
    input_file = sys.argv[2]
    coverage_output = sys.argv[3] if len(sys.argv) > 3 else "coverage_tmp.json"

    # runpy.run_path устанавливает co_filename ровно в тот путь, который
    # ему передали (например "target.py"), а НЕ в resolved-абсолютный путь.
    # Поэтому сравниваем как есть, без .resolve().
    covered_lines = set()

    def trace_calls(frame, event, arg):
        if event == "line":
            if frame.f_code.co_filename == target_script:
                covered_lines.add(frame.f_lineno)
        return trace_calls

    sys.argv = [target_script, input_file]
    sys.settrace(trace_calls)

    exit_code = 0
    try:
        runpy.run_path(target_script, run_name="__main__")
    except SystemExit as e:
        exit_code = e.code if isinstance(e.code, int) else 1
    except Exception:
        traceback.print_exc()
        exit_code = 1
    finally:
        sys.settrace(None)

    Path(coverage_output).write_text(json.dumps(sorted(covered_lines)))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()