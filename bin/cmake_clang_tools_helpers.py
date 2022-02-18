import glob
from pathlib import Path
from shutil import copyfile
import sys
from typing import List
import yaml

WHITELIST_KEY = 'whitelist'
BLACKLIST_KEY = 'blacklist'
RUN_KEY_PREFIX = 'run_'
TRIGGER_CONTENT = 'RUN'


def load_yaml(path: Path) -> dict:
    """
    Load the YAML file and return a dictionary with the YAML content.
    Exits the program if something goes wrong during the loading or parsing.
    :param path: Path of the YAML file.
    :return: Dictionary containing the YAML content.
    """
    try:
        with open(path, 'r') as file:
            return yaml.safe_load(file)
    except (OSError, IOError) as file_error:
        sys.exit(f"YAML file '{path}' can not be opened: {file_error}")
    except yaml.YAMLError as yaml_error:
        sys.exit(f"YAML file '{path}' can not be parsed: {yaml_error}")


def should_tool_run_for_project(project_name: str, tool_name: str, settings: dict) -> bool:
    """
    Check if the given tool should be run for the given project.
    :param project_name: Project name to check.
    :param tool_name: Name of the clang tool.
    :param settings: YAML node containing the current settings.
    :return: True, if the tool should be run.
    """
    run_tool_key = RUN_KEY_PREFIX + tool_name
    should_run_tool = settings.get(run_tool_key, True)
    whitelist = settings.get(WHITELIST_KEY, list())
    # Empty white list special case, pass all.
    project_is_whitelisted = (project_name in whitelist) or not whitelist
    blacklist = settings.get(BLACKLIST_KEY, list())
    project_is_blacklisted = project_name in blacklist
    should_run_tool_for_project = should_run_tool and project_is_whitelisted and not project_is_blacklisted
    return should_run_tool_for_project


def write_trigger(trigger_path: Path, trigger: bool) -> None:
    """
    Create/Update the trigger file.
    :param trigger_path: Trigger file path.
    :param trigger: True, if the trigger file should contain the trigger content. False, if trigger file shall be empty.
    """
    try:
        with open(trigger_path, 'w') as trigger_file:
            if trigger:
                trigger_file.write(TRIGGER_CONTENT)
    except (OSError, IOError) as file_error:
        sys.exit(f"Trigger file '{trigger_file}' could not be written: {file_error}")


def check_trigger(trigger_path: Path) -> bool:
    """
    Check if the trigger file contains the trigger content.
    :param trigger_path: Trigger file path.
    :return: True, if the trigger file contains the trigger content.
    """
    try:
        with open(trigger_path, 'r') as trigger_file:
            return trigger_file.readline() == TRIGGER_CONTENT
    except (OSError, IOError) as file_error:
        sys.exit(f"Trigger file '{trigger_file}' could not be read: {file_error}")


def update_cache(source_file: str, cache_file: str) -> None:
    """
    Update the cache by copying the source file.
    :param source_file: Original input file.
    :param cache_file: Cache output file.
    """
    copyfile(source_file, cache_file)


def glob_paths(paths: List[str]) -> List[Path]:
    """
    Glob the input paths for files.
    :param paths: Paths to glob.
    :return: List of globed files.
    """
    files = set()
    for pattern in paths:
        for file in glob.iglob(pattern):
            files.add(Path(file))
    return list(files)


def string_to_list(string: str, separator=',') -> List[str]:
    """
    Convert string separated with 'separator' to a list.
    :param string: 'separator'-separated string.
    :param separator: Separator to use. Default is comma-separated.
    :return: list of string
    """
    # The filter ensures that we do not use empty strings.
    return [s.strip() for s in list(filter(None, string.split(separator)))]
