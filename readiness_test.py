#!/usr/bin/env python3

import getpass
import json
import os
import subprocess
import sys
from typing import Any, Callable, TypedDict

# Check if Nix is installed
try:
    subprocess.check_output(["nix", "--version"])
except OSError:
    print("Error: Nix is not installed on this system.")
    sys.exit(1)

RequiredAttrs = TypedDict('RequiredAttrs', {
    "experimental-features": list[str],
})


def get_required_attributes() -> RequiredAttrs:
    return {
        "experimental-features": ['test', 'nix-command', 'flakes'],
    }


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


# Check Nix config
def check_attr(
        nix_conf_json: dict[str, Any],
        attribute: str, pred: Callable[[Any],
                                       tuple[bool, Any]],
        error_details: str):
    attr_val = nix_conf_json[attribute]["value"]
    passed, extra_data = pred(attr_val)
    print_report(attribute, passed)
    if not passed:
        print_fail(ind2(error_details))

    return (passed, extra_data)


def check_trusted_user(nix_conf_json: dict[str, Any]) -> bool:
    user = getpass.getuser()
    err = f"'trusted-users = root {user}' is missing in nix.conf."
    passed, _ = check_attr(
        nix_conf_json,
        "trusted-users",
        lambda users: ("root" in users and user in users, None),
        err)

    return passed


def check_flag_attr(nix_conf_json: dict[str, Any], attribute: str) -> bool:
    err = f"'{attribute} = true' missing in nix.conf."
    passed, _ = check_attr(nix_conf_json, attribute, lambda v: (v, None), err)

    return passed


def check_set_attr(
        nix_conf_json: dict[str, Any],
        attribute: str, required: list[str]) -> bool:
    def pred(attr_val: list[str]) -> tuple[bool, set[str]]:
        cur_set = set(attr_val)
        req_set = set(required)
        return (req_set.issubset(cur_set), req_set.difference(cur_set))

    err = f"The following {attribute} are missing in nix.conf:\n"
    passed, missing = check_attr(nix_conf_json, attribute, pred, err)

    if not passed:
        for val in missing:
            print_fail(ind(f"{val}", 3))
        print("")

    return passed


def check_nix_conf() -> bool:
    print_neutral(f'\n{ind("> Checking nix.conf...")}')
    nix_conf_output = subprocess.check_output(["nix", "show-config", "--json"])
    nix_conf_json = json.loads(nix_conf_output)
    req_attributes = get_required_attributes()
    passed = all([
        check_trusted_user(nix_conf_json),
        check_set_attr(nix_conf_json, "experimental-features",
                       req_attributes["experimental-features"]),
    ])

    return passed


def test_readiness() -> None:
    passed = check_nix_conf()

    if passed:
        print_success(
            f'\n{ind("All checks passed. Installing cardano-node and cardano-cli...")}\n')
    else:
        print_fail(
            f'\n{ind("Nix configuration error: correct the issue(s) above and try again (See README for help).")}\n')
        sys.exit(1)


test_readiness()