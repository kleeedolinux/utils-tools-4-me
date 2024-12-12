#!/usr/bin/env python3
import os
import sys
import random
import argparse
from pathlib import Path

class SecureFileShredder:
    def __init__(self, passes=3):
        """Initialize with number of overwrite passes."""
        self.passes = passes
        # Different patterns for overwriting
        self.patterns = [
            lambda size: b'\x00' * size,  # All zeros
            lambda size: b'\xFF' * size,  # All ones
            lambda size: bytes(random.getrandbits(8) for _ in range(size))  # Random
        ]

    def secure_delete_file(self, file_path):
        """Securely delete a file by overwriting it multiple times."""
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False

            file_size = os.path.getsize(file_path)
            
            # Get the real path in case it's a symbolic link
            real_path = os.path.realpath(file_path)
            
            print(f"Securely deleting: {file_path}")
            print(f"File size: {file_size} bytes")
            
            # Open file in read+write binary mode
            with open(real_path, "r+b") as f:
                # Multiple overwrite passes
                for pass_num in range(self.passes):
                    print(f"Pass {pass_num + 1}/{self.passes}...")
                    
                    # Use different patterns for each pass
                    pattern = self.patterns[pass_num % len(self.patterns)](file_size)
                    
                    # Overwrite file content
                    f.seek(0)
                    f.write(pattern)
                    f.flush()
                    os.fsync(f.fileno())
                
                # Final random overwrite
                f.seek(0)
                f.write(bytes(random.getrandbits(8) for _ in range(file_size)))
                f.flush()
                os.fsync(f.fileno())
            
            # Truncate to 0 bytes
            with open(real_path, "w") as f:
                f.truncate(0)
            
            # Rename file multiple times before deletion
            temp_path = real_path
            for i in range(3):
                new_path = f"{temp_path}.{random.randbytes(8).hex()}"
                os.rename(temp_path, new_path)
                temp_path = new_path
            
            # Finally delete the file
            os.remove(temp_path)
            
            print(f"File has been securely deleted: {file_path}")
            return True

        except Exception as e:
            print(f"Error during secure deletion: {str(e)}")
            return False

    def secure_delete_directory(self, dir_path):
        """Recursively and securely delete a directory and its contents."""
        try:
            if not os.path.exists(dir_path):
                print(f"Directory not found: {dir_path}")
                return False

            # First, recursively handle all contents
            for root, dirs, files in os.walk(dir_path, topdown=False):
                # Delete files first
                for name in files:
                    file_path = os.path.join(root, name)
                    self.secure_delete_file(file_path)
                
                # Then delete empty directories
                for name in dirs:
                    dir_to_remove = os.path.join(root, name)
                    try:
                        os.rmdir(dir_to_remove)
                    except:
                        pass
            
            # Finally remove the root directory
            try:
                os.rmdir(dir_path)
                print(f"Directory has been securely deleted: {dir_path}")
                return True
            except:
                print(f"Could not remove root directory: {dir_path}")
                return False

        except Exception as e:
            print(f"Error during directory deletion: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Secure File Shredder - Permanently delete files beyond recovery"
    )
    parser.add_argument(
        "paths",
        nargs='+',
        help="Files or directories to securely delete"
    )
    parser.add_argument(
        "-p",
        "--passes",
        type=int,
        default=3,
        help="Number of overwrite passes (default: 3)"
    )
    args = parser.parse_args()

    shredder = SecureFileShredder(passes=args.passes)
    
    print("WARNING: Files will be PERMANENTLY and IRRECOVERABLY deleted!")
    confirmation = input("Are you sure you want to continue? (yes/no): ")
    
    if confirmation.lower() != 'yes':
        print("Operation cancelled.")
        sys.exit(0)

    for path in args.paths:
        if os.path.isfile(path):
            shredder.secure_delete_file(path)
        elif os.path.isdir(path):
            shredder.secure_delete_directory(path)
        else:
            print(f"Path not found: {path}")

if __name__ == "__main__":
    main() 