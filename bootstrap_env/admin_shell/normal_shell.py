import os
import sys
from pathlib import Path

# Bootstrap-Env
from bootstrap_env.boot_bootstrap_env import (
    Cmd2, VerboseSubprocess, __version__, get_pip_file_name, in_virtualenv
)


class AdminShell(Cmd2):
    version = __version__

    def __init__(self, package_path, package_name, requirements, *args, **kwargs):
        self.package_path = package_path # /src/bootstrap-env/bootstrap_env/
        self.package_name = package_name # bootstrap_env
        self.requirements = requirements # bootstrap_env.admin_shell.requirements.Requirements instance

        super().__init__(*args, **kwargs)

    #_________________________________________________________________________
    # Normal user commands:

    def do_pytest(self, arg):
        """
        Run tests via pytest
        """
        try:
            import pytest
        except ImportError as err:
            print("ERROR: Can't import pytest: %s (pytest not installed, in normal installation!)" % err)
        else:
            root_path = str(self.package_path)
            print("chdir %r" % root_path)
            os.chdir(root_path)

            args = sys.argv[2:]
            print("Call Pytest with args: %s" % repr(args))
            exit_code = pytest.main(args=args)
            sys.exit(exit_code)

    def do_pip_freeze(self, arg):
        """
        Just run 'pip freeze'
        """
        return_code = VerboseSubprocess("pip3", "freeze").verbose_call(check=False)

    def do_update_env(self, arg):
        """
        Update all packages in virtualenv.

        (Call this command only in a activated virtualenv.)
        """
        if not in_virtualenv():
            self.stdout.write("\nERROR: Only allowed in activated virtualenv!\n\n")
            return

        if sys.platform == 'win32':
            bin_dir_name="Scripts"
        else:
            bin_dir_name = "bin"

        pip3_path = Path(sys.prefix, bin_dir_name, get_pip_file_name()) # e.g.: .../bin/pip3
        if not pip3_path.is_file():
            print("ERROR: pip not found here: '%s'" % pip3_path)
            return

        print("pip found here: '%s'" % pip3_path)
        pip3_path = str(pip3_path)

        return_code = VerboseSubprocess(
            pip3_path, "install", "--upgrade", "pip"
        ).verbose_call(check=False)

        root_path = self.package_path.parent

        # Update the requirements files by...
        if self.requirements.normal_mode:
            # ... update 'bootstrap_env' PyPi package
            return_code = VerboseSubprocess(
                pip3_path, "install", "--upgrade", self.package_name
            ).verbose_call(check=False)
        else:
            # ... git pull bootstrap_env sources
            return_code = VerboseSubprocess(
                "git", "pull", "origin",
                cwd=str(root_path)
            ).verbose_call(check=False)

            return_code = VerboseSubprocess(
                pip3_path, "install", "--editable", ".",
                cwd=str(root_path)
            ).verbose_call(check=False)

        requirement_file_path = str(self.requirements.get_requirement_file_path())

        # Update with requirements files:
        self.stdout.write("Use: '%s'\n" % requirement_file_path)
        return_code = VerboseSubprocess(
            pip3_path, "install",
            "--exists-action", "b", # action when a path already exists: (b)ackup
            "--upgrade",
            "--requirement", requirement_file_path,
            timeout=120  # extended timeout for slow Travis ;)
        ).verbose_call(check=False)

        if not self.requirements.normal_mode:
            # Run pip-sync only in developer mode
            return_code = VerboseSubprocess(
                "pip-sync", requirement_file_path,
                cwd=str(root_path)
            ).verbose_call(check=False)

            # 'reinstall' bootstrap_env editable, because it's not in 'requirement_file_path':
            return_code = VerboseSubprocess(
                pip3_path, "install", "--editable", ".",
                cwd=str(root_path)
            ).verbose_call(check=False)

        self.stdout.write("Please restart %s\n" % self.self_filename)
        sys.exit(0)
