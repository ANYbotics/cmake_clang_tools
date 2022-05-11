#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import List

import cmake_clang_tools_helpers


def execute_clang_tidy(executable, files, config, build_directory, header_filter, error, fix, verbose, checks):
    """
    Run clang-tidy.
    :param executable: The clang-format executable.
    :param files: The files to run clang-tidy on.
    :param config: The clan-tidy configuration string.
    :param build_directory: The build directory where the compile commands are located and the output is stored.
    :param header_filter: Header filter to exclude/include header files.
    :param error: Treat warnings as errors.
    :param fix: Fix the issue detected by clang-tidy.
    :param verbose: If True, print to stderr instead of stdout.
    :param checks: Additional checks to include or exclude.
    :return: Result code of the clang-tidy execution.
    """
    # Create base command.
    command = f"{executable} --config={config} -p={build_directory} --header-filter=\"{header_filter}\" " \
              f"--export-fixes={build_directory}/clang-tidy-fixes.yaml --extra-arg=-w"

    # Add optional arguments.
    if error:
        command += " --warnings-as-errors='*'"
    if fix:
        command += " --fix"
    if checks:
        command += f" --checks='{checks}'"

    # Run for all files.
    for file in files:
        command += f" {os.path.abspath(file)}"

    stream = sys.stderr if verbose else sys.stdout
    # print(f"Run clang-tidy: {command}")
    return subprocess.run(command, shell=True, stdout=stream, stderr=stream).returncode


def load_config(config_file: str) -> str:
    """
    Load the configuration and return it as a JSON string.
    :param config_file: Path of the config file.
    :return: Parsed configuration file as string or empty string if config_file is empty.
    """
    # Discover .clang-tidy file if no config file is given.
    if not config_file:
        return str()

    config = json.dumps(cmake_clang_tools_helpers.load_yaml(Path(config_file)))
    # Replace double quotes with single quotes
    idx = config.find("Checks") + 7
    config = config[:idx - 1] + config[idx:].replace("\"", "\'", 2)
    # Remove remaining double quotes
    config = config.replace("\"", "")
    config = json.dumps(config)

    return config


def create_header_filter(header_filter: str, header_dirs: List[str], exclude_header_dirs: List[str]) -> str:
    """
    Create the header filter based on the configuration.
    :param header_filter: Header filter to use as fallback.
    :param header_dirs: Header directories to include in the filter.
    :param exclude_header_dirs: Header directories to exclude in the filter.
    :return: Header filter regular expression.
    """

    # Check validity of the settings.
    if header_dirs:
        if header_filter:
            print("[warning]: Header filter will be ignored, '--header-dirs' is set.")
    else:
        if exclude_header_dirs:
            print("[warning]: Header excludes will be ignored, '--header-dirs' is not set.")
        # Return the header filter or match all if not set.
        return header_filter or '.*'

    # Build header filter from directories.
    overload_header_filter = "^"

    # Exclude all directories from exclude_header_dirs with a negative lookahead.
    if exclude_header_dirs:
        overload_header_filter = f"(?!.*{exclude_header_dirs[0]}/"
        for i in range(1, len(exclude_header_dirs)):
            overload_header_filter += f"|{exclude_header_dirs[i]}/"
        overload_header_filter += ")"

    # Add all header directories to include.
    if header_dirs:
        overload_header_filter += f"({header_dirs[0]}/"
        for i in range(1, len(header_dirs)):
            overload_header_filter += f"|{header_dirs[i]}/"
        overload_header_filter += ")"

    # Remainder can be arbitrary.
    overload_header_filter += ".*$"

    return overload_header_filter




def parse_arguments() -> argparse.Namespace:
    """
    Parses the command line arguments.
    :return: Namespace object that contains the parsed arguments.
    """

    parser = argparse.ArgumentParser(description="Run clang-tidy on the given files.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--clang-tidy", default="clang-tidy", help="The clang-tidy executable.")
    parser.add_argument("--config-file", help="The clang-tidy configuration file. When the value is empty, clang-tidy will attempt to find "
                                              "a file named .clang-tidy for each source file in its parent directories.")
    parser.add_argument("--trigger-file", default=None, help="The trigger file defines if clang-tidy should run."
                                                             "If no trigger file is provided, clang-tidy will be executed.")
    parser.add_argument("--build-directory", help="Directory where the 'compile_commands.json' file is located."
                                                  "Fixes are exported as 'clang-tidy-fixes.yaml' to this directory.")
    parser.add_argument("--header-dirs", help="Comma-separated list of header directories to check.")
    parser.add_argument("--exclude-header-dirs", help="Comma-separated list of excluded header directories."
                                                      "Note: Has no effect if '--header-dirs' is not set.")
    parser.add_argument("--header-filter", help="Header filter to overload specifications from the config file."
                                                "Note: Has no effect if '--header-dirs' is set.")
    parser.add_argument("--checks", help="Comma-separated list of checks to add or remove.")
    parser.add_argument("--error", action="store_true", help="All warnings are treated as errors.")
    parser.add_argument("--fix", action="store_true", help="Fix the issues discovered by clang-tidy (not recommended).")
    parser.add_argument("--verbose", action="store_true", help="Output is printed to stderr instead of stdout.")
    parser.add_argument("paths", nargs="+", help="File paths for which clang-format should be executed."
                                                 "Globbing is used on the file paths.")

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Only run clang-tidy if no trigger file is given or the trigger file contains the trigger content.
    if args.trigger_file and not cmake_clang_tools_helpers.check_trigger(args.trigger_file):
        print("[clang-tidy] Skipping, trigger file not set.")
        sys.exit(0)

    # Construct the header filter.
    header_dirs = cmake_clang_tools_helpers.string_to_list(args.header_dirs)
    exclude_header_dirs = cmake_clang_tools_helpers.string_to_list(args.exclude_header_dirs)
    header_filter = create_header_filter(args.header_filter, header_dirs, exclude_header_dirs)
    config = load_config(args.config_file)

    # Execute clang-tidy.
    result = execute_clang_tidy(args.clang_tidy, args.paths, config, args.build_directory, header_filter, args.error,
                                args.fix, args.verbose, args.checks)
    sys.exit(result)


if __name__ == "__main__":
    main()
