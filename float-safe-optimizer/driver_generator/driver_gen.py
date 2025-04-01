import re
import sys
import os
import subprocess
from typing import Dict, List, Any, Tuple
from parser import parse_c_function, parse_rise_array_sizes, ParsingError
from code_generator import generate_driver


def ensure_out_dir():
    """Create the out directory if it doesn't exist."""
    out_dir = "out"
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def compile_rise_to_c(rise_file_path: str) -> str:
    """
    Compile a RISE program to C code using the compile.sh script.
    Returns the path to the generated C file.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    compile_script = os.path.join(script_dir, "compile.sh")

    try:
        # Make sure the compile script is executable
        os.chmod(compile_script, 0o755)

        # Run the compile script
        result = subprocess.run(
            [compile_script, rise_file_path], capture_output=True, text=True, check=True
        )

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


def main():
    """Main entry point for the driver generator."""
    if len(sys.argv) != 2:
        print("Usage: python driver_gen.py <input_rise_file>")
        print("Example: python driver_gen.py program.rise")
        sys.exit(1)

    rise_file = sys.argv[1]
    out_dir = ensure_out_dir()

    try:
        # First, read the RISE code
        with open(rise_file, "r") as f:
            rise_code = f.read()

        # Compile RISE to C
        print(f"Compiling {rise_file} to C...")
        c_file = compile_rise_to_c(rise_file)
        print(f"Successfully compiled to {c_file}")

        # Read the generated C code
        with open(c_file, "r") as f:
            c_code = f.read()

    except FileNotFoundError as e:
        print(f"Error: Could not find file '{e.filename}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error during compilation: {str(e)}")
        sys.exit(1)

    try:
        parsed_info_c = parse_c_function(c_code)
        parsed_info_rise = parse_rise_array_sizes(rise_code)
    except (ParsingError, ValueError) as e:
        print(f"Error parsing C code: {e}")
        sys.exit(1)

    # Generate the driver code
    driver_code = generate_driver(parsed_info_c, rise_code)

    # Write the driver code to a file in the out directory
    output_file = os.path.join(out_dir, "driver.c")

    with open(output_file, "w") as f:
        f.write(driver_code)

    print(f"Successfully generated {output_file}")

    # Compile the driver with gcc
    try:
        executable_name = os.path.join(out_dir, "driver")
        cmd = ["gcc", "-o", executable_name, output_file, c_file, "-lm"]
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
