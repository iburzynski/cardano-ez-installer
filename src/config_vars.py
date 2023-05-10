import json
import os
import sys
import urllib.request
from typing import Callable, NoReturn, TypedDict

from .utils import ind, print_fail, print_neutral, print_success


ConfigVars = TypedDict('ConfigVars', {
    'NETWORK': str,
    'NETWORK_MAGIC': str,
    'NODE_RELEASE': str,
    'CARDANO_PATH': str,
    'CARDANO_SRC_PATH': str,
    'TESTNET_NAME': str
})


def get_var(var: str, validate: Callable[[str],
                                         str | None]) -> tuple[str | None, str |
                                                               None]:
    val = os.environ.get(var)
    if not val:
        return (None, "not exported in .env")
    err = validate(val)
    return (val if not err else None, err)


def check_network_var(val: str) -> str | None:
    passed = val in ['mainnet', 'testnet']

    return None if passed else "value must be \"mainnet\" or \"testnet\"."


def check_network_magic_var(val: str) -> str | None:
    passed = int(val) in [1, 2]

    return None if passed else "value must be 1 or 2."


def check_node_release_var(val: str) -> str | None:
    tags_url = f"https://api.github.com/repos/input-output-hk/cardano-node/releases"
    req = urllib.request.Request(tags_url)
    req.add_header("User-Agent", "Mozilla/5.0")

    try:
        with urllib.request.urlopen(req) as response:
            data = response.read().decode()
            releases = json.loads(data)
            tags = [release["tag_name"] for release in releases]
            err = None if val in tags else f"{val} is not a valid tag."

            return err

    except:
        return ("unable to validate due to API error.")


def check_path_var(val: str) -> str | None:
    if not os.path.exists(val):
        try:
            os.mkdir(val)
        except OSError as e:
            return (f"unable to create directory ({e})")
    return None


def make_cfg() -> ConfigVars | NoReturn:
    print_neutral(f'\n{ind("> Checking .env variables...")}')
    var_checks = {
        'NETWORK': check_network_var,
        'NETWORK_MAGIC': check_network_magic_var,
        'NODE_RELEASE': check_node_release_var,
        'CARDANO_SRC_PATH': check_path_var,
        'CARDANO_PATH': check_path_var,
    }
    cfg = {}
    all_valid = True
    for var, validate in var_checks.items():
        val, err = get_var(var, validate)
        if val:
            print_success(ind(f"> {var}: PASSED"))
            cfg[var] = val
        else:
            print_fail(ind(f"> {var}: {err}"))
            all_valid = False

    if not all_valid:
        print_fail(
            f'\n{ind(".env variables error: correct the issue(s) above and try again (See README for help).")}\n')
        sys.exit(1)

    cfg['TESTNET_NAME'] = 'preprod' if int(
        cfg['NETWORK_MAGIC']) == 1 else 'preview'

    return {
        'NETWORK': cfg['NETWORK'],
        'NETWORK_MAGIC': cfg['NETWORK_MAGIC'],
        'NODE_RELEASE': cfg['NODE_RELEASE'],
        'CARDANO_PATH': cfg['CARDANO_PATH'],
        'CARDANO_SRC_PATH': cfg['CARDANO_SRC_PATH'],
        'TESTNET_NAME': cfg['TESTNET_NAME']
    }
