# ZipExcept

A Python utility that creates tar or zip archives while respecting `.tarignore` files.

## Purpose

ZipExcept takes the name of a tar or zip file and a source directory, then creates an archive that:

- Maintains the directory structure of the source
- Excludes files, directories, and wildcards patterns found in the `.tarignore` file
- Works recursively through all subdirectories
- Preserves relative paths in the archive

## Features

- Create uncompressed `.tar` or compressed `.tar.gz` archives
- Create `.zip` archives
- Respect `.tarignore` file patterns (similar to `.gitignore`)
- Skip directories/files that match the patterns in `.tarignore`
- Support for wildcard patterns (`*`, `?`, character classes)
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
# Create an uncompressed tar archive
zipexcept -o output.tar -f tar /path/to/directory

# Create a compressed tar.gz archive
zipexcept -o output.tar.gz -f tar -c /path/to/directory

# Create a zip archive
zipexcept -o output.zip -f zip /path/to/directory

# Use a custom .tarignore file
zipexcept -o output.tar -i custom.tarignore /path/to/directory
```

### Command-line options

- `source_dir`: The source directory to archive
- `-o, --output`: Name of the output archive file
- `-f, --format`: Archive format (`tar` or `zip`), defaults to `tar`
- `-c, --compress`: Compress the tar archive (creates .tar.gz file)
- `-i, --ignore-file`: Path to the ignore file, defaults to `.tarignore`

## .tarignore file format

The `.tarignore` file format is similar to `.gitignore`:

```
# Comments start with #
*.log          # Ignore all log files
temp/          # Ignore the temp directory
**/venv/       # Ignore venv directories at any level
build/*        # Ignore everything in the build directory
```

## Examples

### Ignoring virtual environments in multiple locations

To ignore all Python virtual environment directories regardless of where they appear:

```
# Add to .tarignore
**/venv/
**/env/
**/__pycache__/
```

### Creating a source distribution excluding development files

```bash
zipexcept -o myproject.tar.gz -c ~/projects/myproject -i ~/projects/myproject/.tarignore
```

## License

MIT License