# ZipExcept

A Python utility that creates tar or zip archives while respecting `.tarignore` files.

## Features

- Create `.tar.gz` or `.zip` archives from multiple directories recursively
- Respect `.tarignore` file patterns (similar to `.gitignore`)
- Skip directories/files that match the patterns in `.tarignore`
- Support for wildcard patterns
- Simple command-line interface

## Installation

### From source

```bash
git clone https://github.com/yourusername/zipexcept.git
cd zipexcept
pip install -e .
```

## Usage

```bash
# Create a tar archive
zipexcept -o output.tar.gz -f tar directory1 directory2 file1

# Create a zip archive
zipexcept -o output.zip -f zip directory1 directory2

# Use a custom .tarignore file
zipexcept -o output.tar.gz -i custom.tarignore directory1
```

### Command-line options

- `sources`: One or more source files/directories to archive
- `-o, --output`: Name of the output archive file
- `-f, --format`: Archive format (`tar` or `zip`), defaults to `tar`
- `-i, --ignore-file`: Path to the ignore file, defaults to `.tarignore`

## .tarignore file format

The `.tarignore` file format is similar to `.gitignore`:

```
# Comments start with #
*.log       # Ignore all log files
temp/       # Ignore the temp directory
build/*     # Ignore everything in the build directory
```

## License

MIT License