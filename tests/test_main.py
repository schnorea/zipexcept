import os
import tempfile
import unittest
import zipfile
import tarfile
import shutil
from pathlib import Path

from zipexcept.main import create_archive, read_tarignore, should_exclude


class TestZipExcept(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files and directories
        os.makedirs(os.path.join(self.test_dir, "include_dir"))
        os.makedirs(os.path.join(self.test_dir, "exclude_dir"))
        os.makedirs(os.path.join(self.test_dir, "mixed_dir"))
        
        with open(os.path.join(self.test_dir, "include_file.txt"), "w") as f:
            f.write("include")
        
        with open(os.path.join(self.test_dir, "exclude_file.log"), "w") as f:
            f.write("exclude")
            
        with open(os.path.join(self.test_dir, "mixed_dir", "include.txt"), "w") as f:
            f.write("include")
            
        with open(os.path.join(self.test_dir, "mixed_dir", "exclude.log"), "w") as f:
            f.write("exclude")
        
        # Create a .tarignore file
        with open(os.path.join(self.test_dir, ".tarignore"), "w") as f:
            f.write("*.log\nexclude_dir/\n")
    
    def tearDown(self):
        # Clean up temp directory
        shutil.rmtree(self.test_dir)
    
    def test_read_tarignore(self):
        """Test that .tarignore file is read correctly"""
        patterns = read_tarignore(os.path.join(self.test_dir, ".tarignore"))
        self.assertEqual(patterns, ["*.log", "exclude_dir/"])
    
    def test_should_exclude(self):
        """Test that should_exclude correctly identifies excluded patterns"""
        patterns = ["*.log", "exclude_dir/"]
        
        # Should be excluded
        self.assertTrue(should_exclude(
            os.path.join(self.test_dir, "exclude_file.log"), 
            self.test_dir, patterns))
        self.assertTrue(should_exclude(
            os.path.join(self.test_dir, "exclude_dir"),
            self.test_dir, patterns))
        
        # Should be included
        self.assertFalse(should_exclude(
            os.path.join(self.test_dir, "include_file.txt"),
            self.test_dir, patterns))
        self.assertFalse(should_exclude(
            os.path.join(self.test_dir, "include_dir"),
            self.test_dir, patterns))
    
    def test_create_zip_archive(self):
        """Test creating a zip archive with exclusions"""
        output = os.path.join(self.test_dir, "output.zip")
        create_archive(
            output, 
            "zip", 
            self.test_dir, 
            os.path.join(self.test_dir, ".tarignore")
        )
        
        # Verify the zip file was created
        self.assertTrue(os.path.exists(output))
        
        # Check contents
        with zipfile.ZipFile(output) as zipf:
            files = zipf.namelist()
            # Files that should be included
            self.assertIn("include_file.txt", files)
            self.assertIn("mixed_dir/include.txt", files)
            
            # Files/dirs that should be excluded
            self.assertNotIn("exclude_file.log", files)
            self.assertNotIn("mixed_dir/exclude.log", files)
            self.assertNotIn("exclude_dir/", files)
    
    def test_create_tar_archive(self):
        """Test creating a tar archive with exclusions"""
        output = os.path.join(self.test_dir, "output.tar.gz")
        create_archive(
            output, 
            "tar", 
            self.test_dir, 
            os.path.join(self.test_dir, ".tarignore"),
            compress=True
        )
        
        # Verify the tar file was created
        self.assertTrue(os.path.exists(output))
        
        # Check contents
        with tarfile.open(output, "r:gz") as tar:
            files = tar.getnames()
            # Files that should be included
            self.assertTrue(any("include_file.txt" in f for f in files))
            self.assertTrue(any("mixed_dir/include.txt" in f for f in files))
            
            # Files/dirs that should be excluded
            self.assertFalse(any("exclude_file.log" in f for f in files))
            self.assertFalse(any("mixed_dir/exclude.log" in f for f in files))
            self.assertFalse(any("exclude_dir" in f for f in files))


if __name__ == "__main__":
    unittest.main()