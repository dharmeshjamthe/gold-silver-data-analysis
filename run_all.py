import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "daily_data.py",
    "data_fetch.py",
    "full_insert.py",
    "smart_agent.py",
]

def run_script(path):
    print(f"\n=== Running: {path} ===")
    proc = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
    print(proc.stdout)
    if proc.stderr:
        print("--- STDERR ---")
        print(proc.stderr)
    print(f"Exit code: {proc.returncode}")
    return proc.returncode


def main():
    base = Path(__file__).parent
    codes = []
    for s in SCRIPTS:
        p = base / s
        if not p.exists():
            print(f"Script not found: {p}")
            codes.append(1)
            continue
        codes.append(run_script(p))

    if any(c != 0 for c in codes):
        print("\nOne or more scripts failed. See above logs.")
        sys.exit(1)
    else:
        print("\nAll scripts completed successfully.")

if __name__ == '__main__':
    main()
