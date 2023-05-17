#!/usr/bin/env python

"""
RS_INSTALL

Installs the suite of R_S internal tools and configures access to
our cluster and shared storage.

Notes:
- python2/python3
- mac/ubuntu
- detects Apple Silicon compatibility
- detects coreweave network
"""

from __future__ import print_function

import datetime
import logging
import os
import shutil
import stat
import subprocess
import sys
import re
from sys import platform

initial_dir = os.getcwd()

is_py3 = sys.version_info[0] == 3
if is_py3:
    from pathlib import Path
    from shutil import which
else:
    from distutils.spawn import find_executable as which


def get_run_returncode(cmd):
    logger.info(">>> " + cmd.lstrip())
    if is_py3:
        result = subprocess.run(cmd, shell=True, executable="/bin/bash")
        return result.returncode
    else:
        return os.system(cmd)


def run(cmd):
    code = get_run_returncode(cmd)
    if code != 0:
        logger.error("Command failed: '%s'", cmd)
        sys.exit(1)


def get_lines_of_run(cmd):
    try:
        bytes = subprocess.check_output(cmd.split())
        text = bytes.decode("utf-8", errors="ignore")
        return text.splitlines()
    except:
        return ""


def install_cmd(binary, install_cmd):
    if which(binary):
        logger.info("Checking for '%s' command: True", binary)
    else:
        logger.info("Installing %s", binary)
        run(install_cmd)


def home():
    return os.path.expanduser("~")


def is_path_exists(fname):
    if is_py3:
        return Path(fname).exists()
    else:
        return os.path.exists(fname)


def path_join(*args):
    return os.path.join(*args)


def path_resolve(p):
    if is_py3:
        return Path(p).resolve()
    else:
        return os.path.abspath(p)


def ensure_dir(fname):
    if is_py3:
        Path(fname).mkdir(exist_ok=True)
    else:
        if not is_path_exists(fname):
            os.makedirs(fname)


def clone_sync_checkout(package, version=None):
    # go to install dir
    current_dir = os.getcwd()
    os.chdir(top_dir)
    package_dir = path_join(top_dir, package)
    if is_path_exists(package):
        os.chdir(package_dir)
        if get_run_returncode("git diff --quiet HEAD --"):
            raise Exception(
                'Local changes in repo "{}". Stash them before updating.'.format(
                    package
                )
            )

    else:
        if is_gh:
            run("gh repo clone RedesignScience/{}".format(package))
        else:
            run("git clone git@github.com:RedesignScience/{}.git".format(package))

    os.chdir(package_dir)
    # Make sure we're on main/master and not detached commits before syncing
    git_remote_show_lines = get_lines_of_run("git remote show origin")
    prog = re.compile("HEAD branch:\s(\S+)")
    matches = [prog.search(line) for line in git_remote_show_lines if prog.search(line)]
    if not matches:
        raise Exception(
            "Unable to determine default branch for package {} located at {}".format(
                package, package_dir
            )
        )
    default_branch_name = matches[0].group(1)
    run("git checkout {}".format(default_branch_name))
    if is_gh:
        run("gh repo sync")
    else:
        run("git fetch")

    if version is not None:
        run("git checkout {}".format(version))
    os.chdir(current_dir)


# Set global log options
logger = logging.getLogger("rs_install")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(message)s")

name = "rs_install.py"
conda_python_version = "3.8"


# Process args
args = sys.argv[1:]

if len(args) > 3:
    logger.error(
        "Usage: rs_install.py <optional: env> <optional: top_dir> <optional: rs_install_version>"
    )
    sys.exit(1)

env = args[0] if len(args) >= 1 else "rs"
logger.info("Installing to env: {}".format(env))

top_dir = path_resolve(args[1]) if len(args) >= 2 else path_resolve("rs")
logger.info("Installing to top_dir: {}".format(top_dir))

if len(args) == 3 and args[2]:
    rs_install_version = args[2]
else:
    logger.info(
        "Defaulting to latest rs_install_version. "
        "To specify, use: rs_install.py <env> <top_dir> <version>"
    )
    rs_install_version = None
version_str = rs_install_version if rs_install_version else "latest"


# Prepare top_dir for installation
ensure_dir(top_dir)
os.chdir(top_dir)


# Create logging handlers
fileHandler = logging.FileHandler(path_join(top_dir, "rs_install.log"))
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(formatter)

# create stream handler and set options
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.INFO)
streamHandler.setFormatter(formatter)

# add handlers to logger object
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)


# Greeting message
print(
    """

*** RS_PUBLIC_INSTALL ***

Install the R_S Toolkit on Ubuntu or Mac

R_S package directory: {}
Python conda environment: `{}`
rs_install version: {}

""".format(
        top_dir, env, version_str
    )
)


# Platform checks
logger.info("### System checks")
is_mac = "darwin" in platform.lower()
if is_mac:
    logger.info("Detected Mac")
    is_apple_silicon = (
        "Apple M" in get_lines_of_run("sysctl -n machdep.cpu.brand_string")[0]
    )
    is_gh = True
    logger.info("Check Apple Silicon-chip: %s", is_apple_silicon)
    if is_apple_silicon:
        try:
            is_rosetta = bool(get_lines_of_run("pgrep oahd"))
        except:
            is_rosetta = False
        logger.info("Check Rosetta: %s", is_rosetta)
        if not is_rosetta:
            logger.info("Installing Rosetta for Apple Silicon macs...")
            run("softwareupdate --install-rosetta")
    brew_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    install_cmd("brew", brew_cmd)
else:
    is_linux = "linux" in sys.platform.lower()
    is_gh = False
    is_apple_silicon = False
    if is_linux:
        logger.info("Detected Linux")
    else:
        logger.error("Couldn't figure out the platform on your machine")
        sys.exit(1)


# Connect to github.com/RedesignScience using gh
if is_gh:
    logger.info("### gh - github authentication")
    install_cmd("gh", "brew install gh")
    # `gh auth status` = 0 if logged in = 1 if not
    if get_run_returncode("gh auth status") != 0:
        run("gh auth login -w -p ssh -h github.com")
        assert get_run_returncode("gh auth status") == 0
    logger.info("Login gh to github.com: True")


# Download rs_install first for package.yaml and env.yaml for conda
logger.info("######################################")
logger.info("### R_S package: rs_install %s", version_str)
clone_sync_checkout("rs_install", rs_install_version)


# Now run the full install
rs_install_py = path_join(top_dir, "rs_install/rs_install.py")
cmd = "python {} {} {}".format(rs_install_py, env, top_dir)
if rs_install_version:
    cmd += f" {rs_install_version}"

run(cmd)
