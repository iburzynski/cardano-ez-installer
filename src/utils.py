import subprocess
import sys
from datetime import datetime


def run(cmd: list[str], err: str) -> None:
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print_fail(ind2(err))
        sys.exit(1)


def run_quiet(cmd: list[str], err: str) -> None:
    try:
        subprocess.run(
            cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True)
    except subprocess.CalledProcessError as e:
        print_fail(ind2(f"{err}: {e.stderr.strip()}"))
        sys.exit(1)


# Formatting helpers
def ind(txt: str, n: int = 1) -> str:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return f"{timestamp}{'  ' * n}{txt}"


def ind2(txt: str) -> str: return ind(txt, 2)


def mk_color_text(
    code: int, txt: str) -> str: return f"\033[{code}m{txt}\033[0m"


def mk_neutral_text(txt: str) -> str: return mk_color_text(93, txt)


def print_success(txt: str) -> None: return print(mk_color_text(92, txt))


def print_success_generic() -> None: return print_success(ind2("* SUCCESS\n"))


def print_neutral(txt: str) -> None: return print(mk_neutral_text(txt))


def print_fail(txt: str) -> None: return print(mk_color_text(91, txt))


def print_report(attr: str, passed: bool) -> None:
    printer = print_success if passed else print_fail
    printer(ind2(f"* {attr}: {'PASSED' if passed else 'FAILED'}"))
