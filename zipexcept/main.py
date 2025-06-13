#!/usr/bin/env python3
"""
ZipExcept - Create tar or zip archives while respecting .tarignore rules

This application creates tar or zip archives of a directory while maintaining the
directory structure but excluding files, directories, and wildcards that match patterns
found in a .tarignore file.
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


def should_exclude(path: str, base_dir: str, patterns: List[str]) -> bool:
    """Determine if a path should be excluded based on the ignore patterns."""
    # Extract the relative path for better pattern matching
    rel_path = os.path.relpath(path, base_dir)
    filename = os.path.basename(path)
    
    for pattern in patterns:
        # Skip empty patterns
        if not pattern:
            continue
            
        # Check directory-specific patterns (ending with /)
        if pattern.endswith('/'):
            if os.path.isdir(path) and fnmatch.fnmatch(rel_path, pattern[:-1] + '*'):
                return True
                
        # Check for wildcard patterns
        elif '*' in pattern or '?' in pattern or '[' in pattern:
            # Match against both relative path and just the filename
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(filename, pattern):
                return True
                
        # Check exact file/dir matches
        elif rel_path == pattern or filename == pattern:
            return True
            
    return False


def collect_files(source_dir: str, ignore_patterns: List[str]) -> Set[str]:
    """
    Recursively collect files from the given source directory, 
    excluding those that match the ignore patterns.
    """
    files_to_include = set()
    source_dir = os.path.abspath(source_dir)
    
    if not os.path.isdir(source_dir):
        print(f"Error: '{source_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)
        
    for root, dirs, files in os.walk(source_dir):
        # Filter directories to avoid traversing excluded ones
        dirs[:] = [d for d in dirs 
                  if not should_exclude(os.path.join(root, d), source_dir, ignore_patterns)]
        
        # Filter files
        for file in files:
            file_path = os.path.join(root, file)
            if not should_exclude(file_path, source_dir, ignore_patterns):
                files_to_include.add(file_path)
    
    return files_to_include


def create_archive(archive_name: str, archive_type: str, 
                  source_dir: str, tarignore_path: Optional[str] = None,
                  compress: bool = False) -> None:
    """
    Create an archive (tar or zip) of the specified source directory,
    respecting the patterns in the .tarignore file.
    
    Args:
        archive_name: Name of the output archive file
        archive_type: Type of archive ('tar' or 'zip')
        source_dir: Source directory to archive
        tarignore_path: Path to the .tarignore file
        compress: Whether to compress the tar archive (for tar only)
    """
    # Read .tarignore patterns if present
    ignore_patterns = []
    if tarignore_path:
        if os.path.exists(tarignore_path):
            ignore_patterns = read_tarignore(tarignore_path)
            print(f"Using ignore patterns from {tarignore_path}")
        else:
            print(f"Warning: .tarignore file '{tarignore_path}' not found.", file=sys.stderr)
    
    # Collect files to include
    files_to_include = collect_files(source_dir, ignore_patterns)
    
    # Get the absolute path of the source directory for path calculations
    source_dir = os.path.abspath(source_dir)
    
    print(f"Creating {archive_type} archive with {len(files_to_include)} files...")
    
    # Create the archive
    if archive_type == 'tar':
        # Use 'w:gz' for compressed tar or 'w' for uncompressed
        mode = 'w:gz' if compress else 'w'
        with tarfile.open(archive_name, mode) as tar:
            for file_path in files_to_include:
                # Preserve directory structure relative to source_dir
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                tar.add(file_path, arcname=arcname)
                print(f"Added: {arcname}", end='\r')
    
    elif archive_type == 'zip':
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_include:
                # Preserve directory structure relative to source_dir
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, arcname=arcname)
                print(f"Added: {arcname}", end='\r')
    
    print(f"\nArchive created successfully: {archive_name}")


def main():
    """Main entry point for the command line interface."""
    parser = argparse.ArgumentParser(
        description="Create tar or zip archives while respecting .tarignore rules."
    )
    parser.add_argument("source_dir", help="Source directory to archive")
    parser.add_argument("-o", "--output", required=True, 
                        help="Name of the output archive file")
    parser.add_argument("-f", "--format", choices=["tar", "zip"], default="tar", 
                        help="Archive format (tar or zip), defaults to tar")
    parser.add_argument("-c", "--compress", action="store_true",
                        help="Compress the tar archive (creates .tar.gz file)")
    parser.add_argument("-i", "--ignore-file", default=".tarignore",
                        help="Path to the .tarignore file (default: .tarignore)")
    
    args = parser.parse_args()
    
    # Add extension if not provided
    if args.format == "tar":
        if args.compress and not args.output.endswith((".tar.gz", ".tgz")):
            args.output += ".tar.gz"
        elif not args.output.endswith(".tar"):
            args.output += ".tar"
    elif args.format == "zip" and not args.output.endswith(".zip"):
        args.output += ".zip"
    
    create_archive(
        args.output, 
        args.format, 
        args.source_dir, 
        args.ignore_file, 
        compress=args.compress
    )


if __name__ == "__main__":
    main()