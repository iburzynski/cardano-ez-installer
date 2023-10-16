import platform
import subprocess
from .utils import ind, print_success


def get_os_info():
    os_name = platform.system()
    if os_name == 'Darwin':
        os_name = 'Mac'
        darwin_version = platform.uname().release
        os_version_name = darwin_to_mac_version(darwin_version)
        return os_name, os_version_name, darwin_version
    else:
        os_version = platform.release()
        return os_name, os_version, None


def get_architecture():
    architecture = platform.machine()
    if architecture == 'x86_64':
        return 'Intel', None
    elif 'arm' in architecture:
        chip_version = get_apple_chip_version()
        return 'Apple Silicon', chip_version
    else:
        return 'Unknown', None


def is_apple_silicon():
    architecture, _ = get_architecture()
    return architecture == 'Apple Silicon'


def get_apple_chip_version():
    try:
        chip_info = subprocess.check_output(
            ['sysctl', '-n', 'machdep.cpu.brand_string'], text=True)
        if 'Apple M1' in chip_info:
            return 'M1'
        elif 'Apple M2' in chip_info:
            return 'M2'
        elif 'Apple M3' in chip_info:
            return 'M3'
        else:
            return 'Unknown'
    except Exception as e:
        print(f"An error occurred: {e}")
        return 'Unknown'


def darwin_to_mac_version(darwin_version):
    major_version = darwin_version.split('.')[0]
    darwin_mac_mapping = {
        '20': 'Big Sur',
        '21': 'Monterey',
        '22': 'Ventura',
        '23': 'Sonoma'
    }
    return darwin_mac_mapping.get(major_version, 'OS not found')


def print_os_info():
    os_name, os_version_name, darwin_version = get_os_info()
    architecture, chip_version = get_architecture()
    if os_name == 'Mac':
        print_success(ind(
            f"Your OS is {os_name} {os_version_name} (Darwin Kernel Version {darwin_version}) on {architecture} with a {chip_version} chip."))
    else:
        print_success(ind(
            f"You OS is {os_name} version {os_version_name} on {architecture} architecture."))
