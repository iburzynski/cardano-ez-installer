import subprocess
import sys


def run_quiet(cmd: list[str], err: str) -> None:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print_fail(ind2(f"{err}: {result.stderr.decode().strip()}"))
        sys.exit(1)


# Formatting helpers
def ind(txt: str, n: int = 1) -> str: return "  " * n + txt
def ind2(txt: str) -> str: return ind(txt, 2)
def mk_color_text(
    code: int, txt: str) -> str: return f"\033[{code}m{txt}\033[0m"


def mk_neutral_text(txt: str) -> str: return mk_color_text(93, txt)
def print_success(txt: str) -> None: return print(mk_color_text(92, txt))
def print_neutral(txt: str) -> None: return print(mk_neutral_text(txt))
def print_fail(txt: str) -> None: return print(mk_color_text(91, txt))


def print_report(attr: str, passed: bool) -> None:
    printer = print_success if passed else print_fail
    printer(ind(f"> {attr}: {'PASSED' if passed else 'FAILED'}"))
