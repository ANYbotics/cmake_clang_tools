#!/usr/bin/env python3

import argparse
from pathlib import Path

import cmake_clang_tools_helpers


def parse_arguments() -> argparse.Namespace:
    """
    Parses the command line arguments.
    :return: Namespace object that contains the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Check if the given clang tool should be run for the given project .")
    parser.add_argument("--tool-name", help="Name of the clang tool.", choices=["clang_tidy", "clang_format"], required=True)
    parser.add_argument("--project-name", help="CMake project name to check.", required=True)
    parser.add_argument("--settings-file", help="Path of the cmake_clang_tools settings file.", type=Path, required=True)
    parser.add_argument("--settings-file-cached", help="Path of the cmake_clang_tools settings cache file to generate.", type=Path,
                        required=True)
    parser.add_argument("--trigger-file", help="Output file path used as a CMake trigger and generated only on setting changes.", type=Path,
                        required=True)
    return parser.parse_args()


def main():
    args = parse_arguments()

    settings = cmake_clang_tools_helpers.load_yaml(args.settings_file)
    cached_settings = cmake_clang_tools_helpers.load_yaml(args.settings_file_cached)

    should_run = cmake_clang_tools_helpers.should_tool_run_for_project(args.project_name, args.tool_name, settings)
    cached_should_run = False
    if cached_settings:
        cached_should_run = cmake_clang_tools_helpers.should_tool_run_for_project(args.project_name, args.tool_name, cached_settings)

    if should_run and not cached_should_run:
        cmake_clang_tools_helpers.write_trigger(args.trigger_file, True)

    cmake_clang_tools_helpers.update_cache(args.settings_file, args.settings_file_cached)


if __name__ == "__main__":
    main()
