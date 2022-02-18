# cmake_clang_tools

# Overview

This package provides cmake helper macros in order to run clang-tidy and clang-format on your code.

It also contains python scripts that wrap around those tools to adapt their behavior.

The source code is released under a [BSD 3-Clause license](LICENSE).

**Author(s):** Gabriel Hottiger

# Installation

## Dependencies
* clang
* clang-tidy
* clang-format

## Build
Both catkin and plain CMake builds are supported.

### Catkin

To build `cmake_clang_tools` with catkin run the following command.

```
  catkin build cmake_clang_tools
```

### CMake

To install `cmake_clang_tools` run the following commands in the root folder of the repository.

```
  mkdir -p build
  cd build
  cmake ..
  make                              # local build
  sudo make install                 # install in /usr/local
```

## Uninstall

To uninstall `cmake_clang_tools` run the following commands in the root folder of the repository.

```
  cd build
  sudo make uninstall               # uninstall from /usr/local
```

# Usage

## Enabling cmake_clang_tools in your project.

In order to use `cmake_clang_tools` in your CMake/catkin project you will have to add the following steps.

#### Package.xml (for catkin only)

```
<build_depend>cmake_clang_tools</build_depend>
```

#### CMakeLists.txt

**Default usage**

The default macro `add_default_clang_tooling` sets reasonable default values for the arguments of `add_clang_tooling`.
It assumes that the source code of the package is located in folders named `src`, `include` and `test`.
This macro will fix formatting issues during compilation.
If all targets are present in the list (`${PROJECT_NAME}`, `${PROJECT_NAME}_core`,
`${PROJECT_NAME}_node`, `test_${PROJECT_NAME}`, `test_${PROJECT_NAME}_core`, `test_${PROJECT_NAME}_node`) the `TARGETS` option can be omitted.

```
# Generate compile_commands.json (needed if clang-tidy is run)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Add your project lib and/or executable (e.g. myLib, myExec)

# Add clang tooling to your target
find_package(cmake_clang_tools QUIET)
if(cmake_clang_tools_FOUND)
  add_default_clang_tooling(
    TARGETS myLib myExec
  )
endif(cmake_clang_tools_FOUND)
```
**Advanced usage**
```
# Generate compile_commands.json (needed if clang-tidy is run)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Add your project lib and/or executable (e.g. myLib, myExec)

# Add clang tooling to your target
find_package(cmake_clang_tools QUIET)
if(cmake_clang_tools_FOUND)
  add_clang_tooling(
    TARGETS myLib myExec
    SOURCE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/src ${CMAKE_CURRENT_SOURCE_DIR}/include
    CT_HEADER_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/include
    CF_FIX
  )
endif(cmake_clang_tools_FOUND)
```

Some example flags were used for the add_clang_tooling cmake macro, see below for a complete list.

## Running cmake_clang_tools

The format checking/fixing (using clang-format) happens before the source code is built and is triggered automatically on every build.

The static analysis (using clang-tidy) has two run behaviors.
Per default, the static analysis is executed when the `run_static_analysis` CMake target is built.
To run static analysis for `my_package` run the following command:

```
catkin build --catkin-make-args run_static_analysis -- my_package --no-deps
```
You can configure clang-tidy to run on every build, by setting the `ATTACH_TO_ALL` option for clang tidy.
This is only recommended in combination with toggling of the `cmake_clang_tools` configuration (described in the next section).
Otherwise, it can lead to significant compile time overhead during the development phase.

## Configure cmake_clang_tools

You can configure `cmake_clang_tools` with a config file located at ```/home/$USER/.config/cmake_clang_tools/config.yaml```. 
The file will be generated with the following default configuration on it's first run.

```
# Toggle execution of clang-format (true/false).
run_clang_format: true
# Toggle execution of clang-tidy (true/false).
run_clang_tidy: true
# Only run cmake_clang_tools for the packages contained in this whitelist.
# Empty list -> run on all packages.
whitelist: { }
# Don't run cmake_clang_tools for the packages contained in this blacklist.
# Empty list -> run on all packages.
blacklist: { }
```

With the first two arguments you can toggle execution of `clang_tidy` and `clang_format`.
This is meant as a temporary solution while developing, since `clang_tidy` can increase compile time quite a bit.

If you only want to run `cmake_clang_tools` on some packages, you can configure a whitelist. 
You can also exclude packages by blacklisting them.
This is useful if you are the maintainer of only a subset of packages that you compile from source.

# Tools

## clang-format

### Disable formatting

To disable formatting temporarily use:
```
Eigen::Matrix2d m;  // clang-format off
m << 2.0, 3.0
     4.0, 5.0;      // clang-format on
```

### .clang-format

The formatting options can be configured with a `.clang-format` file. 

See the [List of Style Options](https://clang.llvm.org/docs/ClangFormatStyleOptions.html).

Current Settings: Check out the `.clang-format` file in the `config` folder.

## clang-tidy

### Disable checks

To disable checks temporarily use:
```
// Silent all the diagnostics for the line
Foo(int param); // NOLINT

// Silent only the specified checks for the line
Foo(double param); // NOLINT(google-explicit-constructor, google-runtime-int)

// Silent only the specified diagnostics for the next line
// NOLINTNEXTLINE(google-explicit-constructor, google-runtime-int)
Foo(bool param);
```

### .clang-tidy

The code check options can be configured with a `.clang-tidy` file.

See the [List of Checks](http://clang.llvm.org/extra/clang-tidy/checks/list.html).

Current Settings: Check out the `.clang-tidy` file in the `config` folder.

# CMake macros

## add_default_clang_tooling
```
ADD_DEFAULT_CLANG_TOOLING(TARGETS target1 .. targetN
                          [SOURCE_DIRS sourceDir1 .. sourceDirN]
                          [DISABLE_CLANG_TIDY]
                          [CT_WERROR]
                          [CT_FIX]
                          [CT_QUIET]
                          [CT_ATTACH_TO_ALL]
                          [CT_CONFIG_FILE ct_config_path]
                          [CT_HEADER_DIRS dir1 .. dirN]
                          [CT_HEADER_EXCLUDE_DIRS excludeDir1 .. excludeDirN]
                          [CT_HEADER_FILTER header_filter]
                          [CT_BUILD_DIR build_dir]
                          [CT_CHECKS check1 .. checkN]
                          [DISABLE_CLANG_FORMAT]
                          [CF_WERROR]
                          [CF_NO_FIX]
                          [CF_QUIET]
                          [CF_CONFIG_FILE cf_config_path])
```
**CF_NO_FIX** Don't fix formatting issues

For the remaining options check the `add_clang_tooling` macro.

## add_clang_tooling
```
ADD_CLANG_TOOLING(TARGETS target1 .. targetN
                  [SOURCE_DIRS sourceDir1 .. sourceDirN]
                  [DISABLE_CLANG_TIDY]
                  [CT_WERROR]
                  [CT_FIX]
                  [CT_QUIET]
                  [CT_ATTACH_TO_ALL]
                  [CT_CONFIG_FILE ct_config_path]
                  [CT_HEADER_DIRS dir1 .. dirN]
                  [CT_HEADER_EXCLUDE_DIRS excludeDir1 .. excludeDirN]
                  [CT_HEADER_FILTER header_filter]
                  [CT_BUILD_DIR build_dir]
                  [CT_CHECKS check1 .. checkN]
                  [DISABLE_CLANG_FORMAT]
                  [CF_WERROR]
                  [CF_FIX]
                  [CF_QUIET]
                  [CF_CONFIG_FILE cf_config_path])
```
**SOURCE_DIRS** Directories for which clang tools are ran

**DISABLE_CLANG_TIDY** Don't run clang-tidy

**DISABLE_CLANG_FORMAT** Don't run clang-format


For the remaining options check the following macros, where CT stands form clang-tidy and CF for clang-format.

## add_clang_format
```
ADD_CLANG_FORMAT(TARGETS target1 .. targetN
                 [SOURCES source1 .. sourceN]
                 [WERROR]
                 [FIX]
                 [QUIET]
                 [CONFIG_FILE config_path])
```
**TARGETS** Targets for which clang-format is ran on POST_BUILD

**SOURCES** Source files to run clang-format on

**WERROR** Treat formatting issues as errors

**FIX** Fix formatting issues inline

**QUIET** Output to stdout instead of stderr

**CONFIG_FILE** Clang-format config file to be used (default: .clang-format in this repo)


## add_clang_tidy
```
ADD_CLANG_TIDY(TARGETS target1 .. targetN
               [SOURCES source1 .. sourceN]
               [WERROR]
               [FIX]
               [QUIET]
               [ATTACH_TO_ALL]
               [CONFIG_FILE config_path]
               [HEADER_DIRS dir1 .. dirN]
               [HEADER_EXCLUDE_DIRS excludeDir1 .. excludeDirN]
               [HEADER_FILTER header_filter]
               [BUILD_DIR build_dir]
               [CHECKS check1 .. checkN])
```
**TARGETS** Targets for which clang-tidy is run on POST_BUILD

**SOURCES** Source files to run clang-tidy on

**WERROR** Treat all clang-tidy warnings as errors

**FIX** Fix clang-tidy issues inline (**Not Recommended!**)

**QUIET** Output to stdout instead of stderr

**ATTACH_TO_ALL** Attach the clang-tidy target to the ALL target. Runs clang-tidy on every build.

**CONFIG_FILE** Clang-tidy config file to be used (default: .clang-tidy in this repo)

**HEADER_DIRS** Header directories, all include directories of your project

**HEADER_EXCLUDE_DIRS** Header directories to exclude from HEADER_DIRS (*Thus HEADER_DIRS must be set!*)

**HEADER_FILTER** Header filter, regular expression (*,|) to filter headers. Only active if HEADER_DIRS are not set. (default: .\*)

**BUILD_DIR** Build directory of the target, compile_commands.json should be located in here. (default: ${CMAKE_CURRENT_BINARY_DIR})

**CHECKS** Add/remove checks to/from the configuration file (default: [])
           Use the check name to add a new check or prefix the check name with `-` to remove it.
           See [list of clang-tidy checks](https://releases.llvm.org/10.0.0/tools/clang/tools/extra/docs/clang-tidy/checks/list.html).


# Editors

## CLion

Clang format and clang tidy are built-in tools in CLion. Add the `.clang-tidy` and `.clang-format` files to the root of your project path.
Jetbrains provides setup instructions for [clang format](https://blog.jetbrains.com/clion/2019/01/clion-opens-2019-1-eap-clangformat-disasm-lldb-injected-languages/#clangformat_support)
and [clang tidy](https://www.jetbrains.com/help/clion/clang-tidy-checks-support.html#conffiles).

## Eclipse

There exist plugins to support clang tooling for eclipse.

### Add clang format as a plugin
[See here](https://marketplace.eclipse.org/content/cppstyle)

### Add clang tidy as a plugin
[See here](https://github.com/Ericsson/CodeCheckerEclipsePlugin)
