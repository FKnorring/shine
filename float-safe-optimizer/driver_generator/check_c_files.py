import os
import sys
import argparse
from typing import Tuple, Optional

def get_expected_c_files(rise_file: str, prefix: str = "", out_dir: str = "out") -> Tuple[str, str, str]:
    """
    Get the expected paths for the three C files based on the RISE file name.
    
    Args:
        rise_file: Path to the RISE source file
        prefix: Optional prefix to add to file names
        out_dir: Directory where C files should be located
        
    Returns:
        Tuple of paths to the expected C files: (unopt, unopt_mpfr, opt)
    """
    # Ensure out_dir is an absolute path
    if not os.path.isabs(out_dir):
        # If path is relative, make it absolute relative to the driver_generator directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(script_dir, out_dir)
    
    # Get base name from the RISE file
    base_name = os.path.basename(rise_file).replace(".rise", "")
    if prefix:
        base_name = f"{prefix}{base_name}"
    
    # Build paths for all three C files
    c_file_unopt = os.path.join(out_dir, f"{base_name}_unopt.c")
    c_file_mpfr_unopt = os.path.join(out_dir, f"{base_name}_mpfr_unopt.c")
    c_file_opt = os.path.join(out_dir, f"{base_name}.c")
    
    return c_file_unopt, c_file_mpfr_unopt, c_file_opt

def check_c_files_exist(rise_file: str, prefix: str = "", out_dir: str = "out") -> Tuple[bool, Optional[str]]:
    """
    Check if all required C files exist for a given RISE file.
    
    Args:
        rise_file: Path to the RISE source file
        prefix: Optional prefix to add to file names
        out_dir: Directory where C files should be located
        
    Returns:
        Tuple of (success, error_message)
        - success: True if all files exist, False otherwise
        - error_message: None if successful, error message if files are missing
    """
    # Ensure out_dir is an absolute path
    if not os.path.isabs(out_dir):
        # If path is relative, make it absolute relative to the driver_generator directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(script_dir, out_dir)
    
    # Get expected file paths
    c_file_unopt, c_file_mpfr_unopt, c_file_opt = get_expected_c_files(rise_file, prefix, out_dir)
    
    # Check each file
    missing_files = []
    for file_path in [c_file_unopt, c_file_mpfr_unopt, c_file_opt]:
        print(f"Checking if {file_path} exists")
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        error_msg = "Missing required C files:\n" + "\n".join(f"- {f}" for f in missing_files)
        return False, error_msg
    
    return True, None

def main():
    """Main entry point for standalone script usage."""
    parser = argparse.ArgumentParser(description='Check if all required C files exist for a RISE file')
    parser.add_argument('rise_file', help='Path to the RISE source file')
    parser.add_argument('--prefix', default='', help='Optional prefix for C file names')
    parser.add_argument('--out-dir', default='out', help='Directory where C files should be located')
    args = parser.parse_args()
    
    success, error_msg = check_c_files_exist(args.rise_file, args.prefix, args.out_dir)
    
    if success:
        print("All required C files exist")
        sys.exit(0)
    else:
        print(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main() 