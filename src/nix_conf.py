# Check Nix config
import getpass
import json
import subprocess
from typing import Any, Callable
from src.utils import ind, ind2, print_fail, print_neutral, print_report


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
    passed = all([
        check_trusted_user(nix_conf_json),
        check_set_attr(nix_conf_json, "experimental-features",
                       ['nix-command', 'flakes']),
    ])
    if not passed:
        print_fail(
            f'\n{ind("Nix configuration error: correct the issue(s) above and try again (See README for help).")}\n')

    return passed
