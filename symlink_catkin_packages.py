#!/usr/bin/python3

import glob

import argparse

import os
import os.path

import typing


def main():
    parser = argparse.ArgumentParser(description='Add "compile_commands.json" files from the "build" directory to the "src" directory of a catkin workspace. Remember to include -DCMAKE_EXPORT_COMPILE_COMMANDS=1 to the catkin config cmake-args. To add this, execute: `catkin config --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=1`')
    parser.add_argument(
        '-p', '--path', default=os.getcwd(),
        help="Path to the catkin workspace (default is current working directory, `os.getcwd()`).",
        type=str
    )

    args = parser.parse_args()

    base_path: typing.Union[str, bytes, os.PathLike] = args.path
    if not os.path.isdir(base_path):
        print("Path does not seem to exist:", base_path)
        return

    compile_command_paths = glob.glob(
        os.path.join(base_path, "build/*/compile_commands.json")
    )
    if len(compile_command_paths) == 0:
        print("Found no compile_commands.json files in the path", os.path.join(base_path, "build/*/compile_commands.json"))
        print("Is the base path", base_path, "correct, and have you built the project?")

    compiled_packages = {os.path.basename(os.path.dirname(path)): path for path in compile_command_paths}
    package_paths = {}

    for root, dirs, files in os.walk(os.path.join(base_path, "src"), followlinks=True):
        for package, path in compiled_packages.items():
            if package in dirs and package not in package_paths.keys():
                project_dir_path = os.path.join(root, package)
                if os.path.exists(os.path.join(project_dir_path, "CMakeLists.txt")):
                    package_paths[package] = project_dir_path
                else:
                    print("Couldn't find a CMakeLists.txt file for", package, "in", project_dir_path)

    intersection = set(compiled_packages.keys()) ^ set(package_paths.keys())
    if len(intersection) > 0:
        print("Couldn't find a matching src package for these builds: ")
        for package in intersection:
            print(package)
        print("If any of these should be accounted for, please ensure that the package directory name and project name are the same. ")

    for package, path in package_paths.items():
        compile_commands_build = os.path.join(path, "build")
        compile_commands_path = os.path.join(compile_commands_build, "compile_commands.json")
        if os.path.exists(compile_commands_path):
            print("compile commands already present for", package, "unlinking and creating new link")
            os.unlink(compile_commands_path)
        else:
            print("missing compile commands for", package)
            if os.path.isdir(compile_commands_build):
                print("linking into existing build folder")
            else:
                print("creating new build folder")
                os.mkdir(compile_commands_build)
        os.symlink(compiled_packages[package], compile_commands_path)


if __name__ == "__main__":
    main()
