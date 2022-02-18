#!/usr/bin/env python3

# Extension of: https://github.com/cloderic/clang_format_check
# Original Author: Clodéric Mars (https://github.com/cloderic)
# Original License: The Unlicense


import argparse
from collections import namedtuple
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ElementTree

import cmake_clang_tools_helpers

"""
Replacement type.
   Attributes:
        offset    Start index in the file content.
        length    Length of the replacement.
        text      Replacement text.
"""
Replacement = namedtuple("Replacement", "offset length text")

"""
Error type.
   Attributes:
        line        Line index in file.
        column      Column index in line.
        found       Found text.
        expected    Expected text.
"""
Error = namedtuple("Error", "line column found expected")

CONFIG_FILE_SEARCH = "file"


def execute_clang_format(executable: str, file: Path, config_file: str, fix: bool) -> str:
    """
    Execute clang-format with the given config on a given file.
    :param executable: The clang-format executable.
    :param file: File to run clang-format on.
    :param config_file: Configuration file to run clang-format with.
    :param fix: If true, formatting errors are fixed inline. If false, the errors are returned as XML output
    :return: Command output. If fix is false, the XML output of clang-format is returned.
    """

    # Check for special case to search file.
    if config_file != CONFIG_FILE_SEARCH:
        config = json.dumps(cmake_clang_tools_helpers.load_yaml(Path(config_file)))
    else:
        config = CONFIG_FILE_SEARCH

    # Run the clang-format executable with the given config.
    command = [executable, f"--style={config}"]

    # Either fix the errors directly or report them as XML output.
    if fix:
        command.append("-i")
    else:
        command.append("--output-replacements-xml")

    # Run on a single file.
    command.append(str(file.resolve()))

    return subprocess.check_output(command)


def parse_replacements_from_xml(xml: str) -> List[Replacement]:
    """
    Create a list of replacements from the XML output of clang-format.
    The replacements are the suggested formatting changes.
    :param xml: XML output of clang-format.
    :return: List of replacements.
    """

    replacements = list()
    if xml:
        replacement_xml = ElementTree.XML(xml)
        for replacement_item in replacement_xml.findall('replacement'):
            replacement = Replacement(offset=int(replacement_item.attrib["offset"]), length=int(replacement_item.attrib["length"]),
                                      text=replacement_item.text)
            replacements.append(replacement)

    return replacements


def convert_replacements_to_errors(file: Path, replacements: List[Replacement]) -> List[Error]:
    """
    Create a list of errors from the replacements of a file.
    The error format is then used for printing compiler warnings/errors.
    :param file: File for which replacements are suggested.
    :param replacements: Replacements from clang-format to convert.
    :return: List of errors corresponding to the replacements.
    """
    errors = list()

    # Content of the file as a string.
    file_content = ""
    # Keep track of the offset in the file content.
    line_offset_indices = [0]

    # Loop through the lines of the file and gather contents and offsets.
    for line in open(file, "r"):
        file_content += line
        line_offset_indices.append(line_offset_indices[-1] + len(line))

    for line_number, line_offset in enumerate(line_offset_indices[:-1]):
        while len(replacements) > 0 and line_offset_indices[line_number + 1] > replacements[0].offset:
            replacement = replacements.pop(0)
            error = Error(line=line_number, column=replacement.offset - line_offset,
                          found=file_content[replacement.offset: replacement.offset + replacement.length],
                          expected=replacement.text if replacement.text else str())
            errors.append(error)

        if len(replacements) == 0:
            break

    return errors


def clang_format_check(executable: str, files: List[Path], config_file: str, fix: bool) -> Tuple[int, Dict[Path, List[Error]]]:
    """
    Run the clang-format check.
    :param executable: The clang-format executable.
    :param files: List of files to run clang-format on.
    :param config_file: Configuration file to run clang-format with.
    :param fix: If true, formatting errors are fixed inline. If false, the errors are returned as XML output
    :return: Tuple of the number of detected errors and a dictionary mapping filename to the list of errors of that file.
    """
    error_count = 0
    file_errors = dict()

    for file in files:
        xml_output = execute_clang_format(executable, file, config_file, fix)
        replacements = parse_replacements_from_xml(xml_output)
        errors = convert_replacements_to_errors(file, replacements)
        error_count += len(errors)
        file_errors[file] = errors

    return error_count, file_errors


def print_error_report(file_errors: Dict[Path, List[Error]], warnings_as_errors: bool, verbose: bool) -> None:
    """
    Print the errors in the form of compiler warnings/errors.
    :param file_errors: Dictionary mapping a filename to the list of errors of that file.
    :param warnings_as_errors: Treat warnings as errors. If True, prints compiler errors instead of compiler warnings (equivalent to gcc's -Werrror flag).
    :param verbose: If True, print to stderr instead of stdout.
    """
    # Select stream base on verbosity.
    stream = sys.stderr if verbose else sys.stdout
    severity = '\033[91merror:' if warnings_as_errors else '\033[35mwarning:'

    # Loop through errors and pretty print them.
    for file, errors in file_errors.items():
        for error in errors:
            file_path = os.path.abspath(file)
            line = error.line + 1
            column = error.column + 1
            found = "\\n".join(error.found.split("\n"))
            expected = "\\n".join(error.expected.split("\n"))
            character_diff = abs(len(error.found) - len(error.expected))
            text = f"\033[1m\033[97m{file_path}:{line}:{column}: {severity}\033[97m clang-format\033[0m  " \
                   f"Found: \'{found}\', Expected: \'{expected}\', CharacterDiff: \'{character_diff}\'"
            print(text, file=stream)


def parse_arguments() -> argparse.Namespace:
    """
    Parses the command line arguments.
    :return: Namespace object that contains the parsed arguments.
    """

    parser = argparse.ArgumentParser(description="Run clang-format on the given files.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--clang-format", default="clang-format", help="The clang-format executable.")
    parser.add_argument("--config-file", default="file",
                        help=f"The clang-format configuration file. Use '{CONFIG_FILE_SEARCH}' to load style configuration  .clang-format "
                             "file located in one of the parent directories of the source file (or current directory for stdin).")
    parser.add_argument("--trigger-file", default=None, help="The trigger file defines if clang-format should run."
                                                             "If no trigger file is provided, clang-format will be executed.")
    parser.add_argument("--error", action="store_true", help="All warnings are treated as errors.")
    parser.add_argument("--fix", action="store_true", help="Fix the formatting issues.")
    parser.add_argument("--verbose", action="store_true", help="Output is printed to stderr instead of stdout.")
    parser.add_argument("paths", nargs="+", help="File paths for which clang-format should be executed."
                                                 "Globbing is used on the file paths.")

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Only run clang-format if no trigger file is given or the trigger file contains the trigger content.
    if args.trigger_file and not cmake_clang_tools_helpers.check_trigger(args.trigger_file):
        print("[clang-format] Skipping, trigger file not set.")
        sys.exit(0)

    # Run clang-format and collect errors.
    all_files = cmake_clang_tools_helpers.glob_paths(args.paths)
    error_count, file_errors = clang_format_check(args.clang_format, all_files, args.config_file, args.fix)

    # Print errors in compiler warning format.
    print_error_report(file_errors, args.error, args.verbose)

    # If warnings should be treated as an error, return the error count.
    if args.error:
        sys.exit(min(1, error_count))


if __name__ == "__main__":
    main()
