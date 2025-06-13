#!/usr/bin/env python3
"""
ZipExcept - Create tar or zip archives while respecting .tarignore rules
"""
import os
import tarfile
import zipfile
import fnmatch
import argparse
import sys
from pathlib import Path
from typing import List, Set, Optional


def read_tarignore(tarignore_path: str) -> List[str]:
    """Read and parse the .tarignore file, returning a list of patterns."""
    if not os.path.exists(tarignore_path):
        return []
    
    with open(tarignore_path, 'r') as f:
        patterns = []
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                patterns.append(line)
    return patterns


def should_exclude(path: str, patterns: List[str]) -> bool:
    """Determine if a path should be excluded based on the ignore patterns."""
    # Convert path to relative path for matching
    rel_path = path
    for pattern in patterns:
        # Check for directory-specific patterns
        if pattern.endswith('/'):
            if os.path.isdir(path) and fnmatch.fnmatch(rel_path, pattern[:-1] + '*'):
                return True
        # Check regular patterns
        elif fnmatch.fnmatch(rel_path, pattern):
            return True
    return False


def collect_files(paths: List[str], ignore_patterns: List[str]) -> Set[str]:
    """
    Recursively collect files from the given paths, 
    excluding those that match the ignore patterns.
    """
    files_to_include = set()
    for path in paths:
        path = os.path.abspath(path)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                # Filter directories to avoid traversing excluded ones
                dirs[:] = [d for d in dirs 
                          if not should_exclude(os.path.join(root, d), ignore_patterns)]
                
                # Filter files
                for file in files:
                    file_path = os.path.join(root, file)
                    if not should_exclude(file_path, ignore_patterns):
                        files_to_include.add(file_path)
        else:
            # Single file
            if not should_exclude(path, ignore_patterns):
                files_to_include.add(path)
    
    return files_to_include


def create_archive(archive_name: str, archive_type: str, 
                  sources: List[str], tarignore_path: Optional[str] = None) -> None:
    """
    Create an archive (tar or zip) of the specified sources,
    respecting the patterns in the .tarignore file.
    """
    # Read .tarignore patterns if present
    ignore_patterns = []
    if tarignore_path:
        if os.path.exists(tarignore_path):
            ignore_patterns = read_tarignore(tarignore_path)
        else:
            print(f"Warning: .tarignore file '{tarignore_path}' not found.", file=sys.stderr)
    
    # Collect files to include
    files_to_include = collect_files(sources, ignore_patterns)
    
    print(f"Creating {archive_type} archive with {len(files_to_include)} files...")
    
    # Create the archive
    if archive_type == 'tar':
        with tarfile.open(archive_name, 'w:gz') as tar:
            base_dirs = set(os.path.dirname(p) for p in sources)
            common_prefix = os.path.commonpath(base_dirs) if len(base_dirs) > 1 else ""
            
            for file_path in files_to_include:
                # Preserve directory structure but make it relative to common prefix
                arcname = os.path.relpath(file_path, common_prefix) if common_prefix else os.path.basename(file_path)
                tar.add(file_path, arcname=arcname)
    
    elif archive_type == 'zip':
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            base_dirs = set(os.path.dirname(p) for p in sources)
            common_prefix = os.path.commonpath(base_dirs) if len(base_dirs) > 1 else ""
            
            for file_path in files_to_include:
                # Preserve directory structure but make it relative to common prefix
                arcname = os.path.relpath(file_path, common_prefix) if common_prefix else os.path.basename(file_path)
                zipf.write(file_path, arcname=arcname)
    
    print(f"Archive created successfully: {archive_name}")


def main():
    """Main entry point for the command line interface."""
    parser = argparse.ArgumentParser(
        description="Create tar or zip archives while respecting .tarignore rules."
    )
    parser.add_argument("sources", nargs='+', help="Source directories or files to archive")
    parser.add_argument("-o", "--output", required=True, 
                        help="Name of the output archive file")
    parser.add_argument("-f", "--format", choices=["tar", "zip"], default="tar", 
                        help="Archive format (tar or zip)")
    parser.add_argument("-i", "--ignore-file", default=".tarignore",
                        help="Path to the .tarignore file (default: .tarignore)")
    
    args = parser.parse_args()
    
    # Add extension if not provided
    if args.format == "tar" and not args.output.endswith((".tar", ".tar.gz")):
        args.output += ".tar.gz"
    elif args.format == "zip" and not args.output.endswith(".zip"):
        args.output += ".zip"
    
    create_archive(args.output, args.format, args.sources, args.ignore_file)


if __name__ == "__main__":
    main()