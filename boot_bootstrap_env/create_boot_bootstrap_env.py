#!/usr/bin/env python
# coding: utf-8

import os
import pprint

from bootstrap_env import create_bootstrap
from bootstrap_env.pip_utils import requirements_definitions


REQ_FILENAMES=(
    "normal_installation.txt",
    "git_readonly_installation.txt",
    "developer_installation.txt",
)

BASE_PATH=os.path.abspath(os.path.join(os.path.dirname(__file__)))

PREFIX_SCRIPT=os.path.abspath(os.path.join(BASE_PATH, "sources", "prefix_code.py"))

REQ_BASE_PATH=os.path.abspath(os.path.join(BASE_PATH, "..", "requirements"))
print("requirement files path: %r" % REQ_BASE_PATH)

if __name__ == '__main__':
    prefix_code = "\n".join([
        requirements_definitions(REQ_BASE_PATH, REQ_FILENAMES),
        create_bootstrap.get_code(PREFIX_SCRIPT, create_bootstrap.INSTALL_PIP_MARK),
    ])

    create_bootstrap.generate_bootstrap(
        out_filename=os.path.join(BASE_PATH, "..", "boot_bootstrap_env.py"),
        add_extend_parser=os.path.join(BASE_PATH, "sources", "extend_parser.py"),
        add_adjust_options=os.path.join(BASE_PATH, "sources", "adjust_options.py"),
        add_after_install=os.path.join(BASE_PATH, "sources", "after_install.py"),
        cut_mark="# --- CUT here ---",
        prefix=prefix_code, # Optional code that will be inserted before extend_parser() code part.
        suffix=None, # Optional code that will be inserted after after_install() code part.
    )