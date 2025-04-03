import re
import sys
import os
import subprocess
import argparse
from typing import Dict, List, Any, Tuple
from parser import parse_c_function, parse_rise_array_sizes, ParsingError
from code_generator import generate_driver


def ensure_out_dir():
    """Create the out directory if it doesn't exist."""
    out_dir = "out"
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def compile_rise_to_c(rise_file_path: str, use_mpfr: bool = False) -> str:
    """
    Compile a RISE program to C code using the compile.sh script.
    Args:
        rise_file_path: Path to the RISE source file
        use_mpfr: Whether to use MPFR for compilation
    Returns:
        The path to the generated C file
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    compile_script = os.path.join(script_dir, "compile.sh")

    try:
        # Make sure the compile script is executable
        os.chmod(compile_script, 0o755)

        # Prepare the command with optional MPFR flag
        cmd = [compile_script, rise_file_path]
        if use_mpfr:
            cmd.append("--mpfr")

        # Run the compile script
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # The last line of output contains the path to the generated C file
        c_file_path = result.stdout.strip().split("\n")[-1]

        if not os.path.exists(c_file_path):
            raise RuntimeError(
                f"C file was not generated at expected path: {c_file_path}"
            )

        return c_file_path

    except subprocess.CalledProcessError as e:
        print("Error during RISE compilation:")
        print(e.stderr)
        raise
    except Exception as e:
        print(f"Error during RISE compilation: {str(e)}")
        raise


def edit_mpfr_function_name(c_file_path: str, function_name: str) -> None:
    """
    Edit the MPFR C file to change the function name to include _mpfr suffix.
    
    Args:
        c_file_path: Path to the MPFR C file
        function_name: The original function name
    """
    try:
        # Read the file content
        with open(c_file_path, 'r') as f:
            content = f.read()
        
        # Replace the function name with function_name_mpfr
        new_content = content.replace(f"void {function_name}(", f"void {function_name}_mpfr(")
        
        # Write the modified content back to the file
        with open(c_file_path, 'w') as f:
            f.write(new_content)
            
        print(f"Successfully renamed function in {c_file_path} from {function_name} to {function_name}_mpfr")
    except Exception as e:
        print(f"Error editing MPFR function name: {e}")
        raise


def main():
    """Main entry point for the driver generator."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate a driver for RISE code with MPFR comparison')
    parser.add_argument('rise_file', help='Path to the RISE source file')
    parser.add_argument('-d', '--dimension', type=int, default=256, 
                        help='Dimension size for all dimensions (default: 256)')
    parser.add_argument('-p', '--precision', type=int, default=256,
                        help='MPFR precision in bits (default: 256)')
    parser.add_argument('-o', '--output', default='driver_compare.c',
                        help='Output driver file name (default: driver_compare.c)')
    args = parser.parse_args()

    rise_file = args.rise_file
    dimension = args.dimension
    precision = args.precision
    output_file_name = args.output
    
    out_dir = ensure_out_dir()

    try:
        # First, read the RISE code
        with open(rise_file, "r") as f:
            rise_code = f.read()

        # Compile RISE to C (both versions)
        print(f"Compiling {rise_file} to C (standard version)...")
        c_file_standard = compile_rise_to_c(rise_file, use_mpfr=False)
        print(f"Successfully compiled to {c_file_standard}")

        print(f"Compiling {rise_file} to C (MPFR version)...")
        c_file_mpfr = compile_rise_to_c(rise_file, use_mpfr=True)
        print(f"Successfully compiled to {c_file_mpfr}")

        # Read both generated C codes
        with open(c_file_standard, "r") as f:
            c_code_standard = f.read()
        with open(c_file_mpfr, "r") as f:
            c_code_mpfr = f.read()

    except FileNotFoundError as e:
        print(f"Error: Could not find file '{e.filename}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error during compilation: {str(e)}")
        sys.exit(1)

    try:
        parsed_info_c_standard = parse_c_function(c_code_standard)
        parsed_info_rise = parse_rise_array_sizes(rise_code)
    except (ParsingError, ValueError) as e:
        print(f"Error parsing C code: {e}")
        sys.exit(1)
        
    # Edit the MPFR C file to change the function name
    function_name = parsed_info_c_standard["name"]
    edit_mpfr_function_name(c_file_mpfr, function_name)

    # Generate comparison driver code with the specified dimension and precision
    driver_code = generate_driver(parsed_info_c_standard, rise_code, dimension, precision)

    # Write the driver code to a file in the out directory
    output_file = os.path.join(out_dir, output_file_name)

    with open(output_file, "w") as f:
        f.write(driver_code)

    print(f"Successfully generated {output_file}")

    # Compile the comparison driver with gcc
    try:
        executable_name = os.path.join(out_dir, os.path.splitext(output_file_name)[0])
        cmd = ["gcc", "-o", executable_name, output_file, c_file_standard, c_file_mpfr, "-lm", "-lmpfr"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully compiled {executable_name}")
        else:
            print("Compilation failed:")
            print(result.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error during compilation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
