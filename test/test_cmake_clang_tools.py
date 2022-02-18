#!/usr/bin/env python3
import filecmp
from pathlib import Path
import sys
from typing import List

# Hack to avoid creating a module.
sys.path.append(str(Path(__file__).resolve().parent.parent / "bin"))
from cmake_clang_tools_helpers import *


def get_settings(run_tidy: bool, run_format: bool, whitelist: List[str], blacklist: List[str]) -> dict:
    return {"run_clang_tidy": run_tidy, "run_clang_format": run_format, "whitelist": whitelist, "blacklist": blacklist}


def test_should_tool_run_for_project_disabled():
    project_name = "project"
    settings = get_settings(False, False, [], [])
    assert not should_tool_run_for_project(project_name, "clang_tidy", settings)
    assert not should_tool_run_for_project(project_name, "clang_format", settings)


def test_should_tool_run_for_project_enabled():
    project_name = "project"
    settings = get_settings(True, True, [], [])
    assert should_tool_run_for_project(project_name, "clang_tidy", settings)
    assert should_tool_run_for_project(project_name, "clang_format", settings)


def test_should_tool_run_for_project_blacklisted():
    project_name = "project"
    project_name2 = "project2"
    settings = get_settings(True, True, [], [project_name])
    assert not should_tool_run_for_project(project_name, "clang_tidy", settings)
    assert not should_tool_run_for_project(project_name, "clang_format", settings)
    assert should_tool_run_for_project(project_name2, "clang_tidy", settings)
    assert should_tool_run_for_project(project_name2, "clang_format", settings)


def test_should_tool_run_for_project_whitelisted():
    project_name = "project"
    project2_name = "project2"
    project3_name = "project3"
    settings = get_settings(True, True, [project_name], [project2_name])
    assert should_tool_run_for_project(project_name, "clang_tidy", settings)
    assert should_tool_run_for_project(project_name, "clang_format", settings)
    assert not should_tool_run_for_project(project2_name, "clang_tidy", settings)
    assert not should_tool_run_for_project(project2_name, "clang_format", settings)
    assert not should_tool_run_for_project(project3_name, "clang_tidy", settings)
    assert not should_tool_run_for_project(project3_name, "clang_format", settings)


def test_should_tool_run_for_project_not_blacklisted():
    project_name = "project"
    settings = get_settings(True, True, [], ["project2"])
    assert should_tool_run_for_project(project_name, "clang_tidy", settings)
    assert should_tool_run_for_project(project_name, "clang_format", settings)


def test_should_tool_run_for_project_not_whitelisted():
    project_name = "project"
    settings = get_settings(True, True, ["project2"], [])
    assert not should_tool_run_for_project(project_name, "clang_tidy", settings)
    assert not should_tool_run_for_project(project_name, "clang_format", settings)


def test_trigger_file_false(tmpdir: Path):
    trigger_file = tmpdir / "test.trigger"
    write_trigger(trigger_file, False)
    assert not check_trigger(trigger_file)


def test_trigger_file_true(tmpdir: Path):
    trigger_file = tmpdir / "test.trigger"
    write_trigger(trigger_file, True)
    assert check_trigger(trigger_file)


def test_update_cache(tmpdir: Path):
    file = tmpdir / "file.yaml"
    cached_file = tmpdir / "cache.yaml"
    with open(cached_file, 'w'):
        pass
    with open(file, 'w') as f:
        f.write("data: {2, 3}")
    assert not filecmp.cmp(file, cached_file)
    update_cache(file, cached_file)
    assert filecmp.cmp(file, cached_file)


def test_string_to_list_default_separator():
    string = "Comma, separated, list"
    expected_list = ['Comma', 'separated', 'list']
    assert expected_list == string_to_list(string)


def test_string_to_list_custom_separator():
    string = "Slash/ separated/ list"
    expected_list = ['Slash', 'separated', 'list']
    assert expected_list == string_to_list(string, '/')


def test_string_to_list_empty():
    string = ""
    expected_list = []
    assert expected_list == string_to_list(string)


def test_string_to_list_extra_separators():
    string = ",a,b,,c,,"
    expected_list = ['a', 'b', 'c']
    assert expected_list == string_to_list(string)


def test_string_to_list_extra_spaces():
    string = "  a   ,  b,c  "
    expected_list = ['a', 'b', 'c']
    assert expected_list == string_to_list(string)
