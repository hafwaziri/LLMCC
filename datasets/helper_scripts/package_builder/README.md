# Debian Package Builder
The Package Builder includes custom scripts to build Debian packages.
The build process is performed in isolated Docker containers.
The builder detects the build system, configuration, build, and test commands for each package, and saves them to a local database. It also builds the packages while ensuring that all dependencies are met.
The Bear tool is used to capture the compilation flags and commands for the source code.
