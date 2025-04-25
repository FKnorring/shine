import re
import sys
import os
import subprocess
import argparse
from typing import Dict, List, Any, Tuple
from parser import parse_c_function, parse_rise_array_sizes, ParsingError
from rise_compile import compile_rise_to_c, edit_function_names
from utils import ensure_out_dir
from c_utils import headers, get_time_func, generate_extern_functions
from c_statistics_utils import generate_statistic_functions
from driver_initialization import generate_initialization_code
from driver_benchmarking import generate_benchmarking_code
from driver_metrics_display import generate_metrics_display_code
from driver_metrics_csv import generate_metrics_csv_code
from driver_cleanup import generate_cleanup_code

def generate_extended_driver(parsed_info: Dict[str, Any], rise_code: str, unopt_file: str, dimension: int = 256, precision: int = 256, float_type: str = "normal", iterations: int = 50, include_negatives: bool = False, metrics_file: str = "metrics.csv", parsed_rise: Dict[str, Any] = None) -> str:
    # Get the base name from the file path
    base_name = os.path.basename(unopt_file).replace("_unopt.c", "")
    
    # Derive file names for the different CSV outputs
    metrics_base = os.path.splitext(metrics_file)[0]
    opt_results_file = f"{metrics_base}_opt_results.csv"
    opt_timings_file = f"{metrics_base}_opt_timings.csv"
    unopt_timings_file = f"{metrics_base}_unopt_timings.csv"
    
    # Add note about negative values if enabled
    neg_note = " with negative values" if include_negatives else ""
    
    driver_code = f"""
{headers}

{get_time_func}

{generate_extern_functions(base_name, parsed_rise["dimensions"], parsed_rise["inputs"])}

{generate_statistic_functions()}

int main(int argc, char** argv) {{
{generate_initialization_code(parsed_rise["dimensions"], dimension, iterations, precision, float_type, include_negatives, parsed_rise)}

  printf("Running benchmarks with {float_type}{neg_note} floating point values...\\n");

{generate_benchmarking_code(base_name, parsed_rise["dimensions"], parsed_rise["inputs"], iterations, precision)}

{generate_metrics_display_code()}

{generate_metrics_csv_code(metrics_file, dimension, float_type, include_negatives, precision, opt_results_file, opt_timings_file, unopt_timings_file)}

{generate_cleanup_code(parsed_rise["dimensions"])}

  return EXIT_SUCCESS;
}}
"""
    return driver_code


def main():
    """Main entry point for the driver generator."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate a driver for RISE code with MPFR comparison')
    parser.add_argument('unopt_rise_file', help='Path to the unoptimized RISE source file')
    parser.add_argument('-o', '--opt_rise_file', help='Path to the optimized RISE source file (optional)')
    parser.add_argument('-d', '--dimension', type=int, default=256, 
                        help='Dimension size for all dimensions (default: 256)')
    parser.add_argument('-i', '--iterations', type=int, default=50,
                        help='Number of iterations for the benchmark (default: 50)')
    parser.add_argument('-p', '--precision', type=int, default=256,
                        help='MPFR precision in bits (default: 256)')
    parser.add_argument('--output', default='driver_compare.c',
                        help='Output driver file name (default: driver_compare.c)')
    parser.add_argument('-f', '--float_type', default='normal', 
                        choices=['normal', 'subnormal', 'mixed', 'magnitude'],
                        help='Type of floating point numbers to generate: normal (default), subnormal, mixed (normal+subnormal), or magnitude (high+low)')
    parser.add_argument('--prefix', default='',
                        help='Prefix to add to all generated files (default: none)')
    parser.add_argument('--include_negatives', action='store_true',
                        help='Include negative numbers in the generated floating-point values')
    parser.add_argument('--metrics_file', default='metrics.csv',
                        help='Output file for performance and accuracy metrics (default: metrics.csv)')
    args = parser.parse_args()

    unopt_rise_file = args.unopt_rise_file
    opt_rise_file = args.opt_rise_file
    dimension = args.dimension
    precision = args.precision
    output_file_name = args.output
    iterations = args.iterations
    float_type = args.float_type
    prefix = args.prefix
    include_negatives = args.include_negatives
    metrics_file = args.metrics_file
    
    out_dir = ensure_out_dir()
    
    # Apply prefix to metrics file name if provided
    if prefix and not metrics_file.startswith(prefix):
        metrics_file = f"{prefix}{metrics_file}"
    
    # Put metrics file in output directory
    metrics_file_path = os.path.join(out_dir, metrics_file)
    
    try:
        # First, read the unoptimized RISE code
        with open(unopt_rise_file, "r") as f:
            unopt_rise_code = f.read()

        # Parse RISE code to get array dimensions
        parsed_rise = parse_rise_array_sizes(unopt_rise_code)

        # Compile RISE to all versions
        print(f"Compiling {unopt_rise_file} to C (all versions)...")
        if opt_rise_file:
            print(f"Using optimized version from {opt_rise_file}")
            c_file_unopt, c_file_mpfr_unopt, c_file_opt = compile_rise_to_c(unopt_rise_file, opt_rise_file, prefix)
        else:
            print("No optimized version provided, using unoptimized for all versions")
            c_file_unopt, c_file_mpfr_unopt, c_file_opt = compile_rise_to_c(unopt_rise_file, None, prefix)
            
        print(f"Successfully compiled to unoptimized: {c_file_unopt}")
        print(f"Successfully compiled to unoptimized MPFR: {c_file_mpfr_unopt}")
        print(f"Successfully compiled to optimized: {c_file_opt}")

        # Rename functions in all files to ensure they have correct names
        edit_function_names(c_file_unopt, c_file_mpfr_unopt, c_file_opt)

        # Read the unoptimized C code for parsing (could use any of the versions)
        with open(c_file_unopt, "r") as f:
            c_code_unopt = f.read()

    except FileNotFoundError as e:
        print(f"Error: Could not find file '{e.filename}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error during compilation: {str(e)}")
        sys.exit(1)

    try:
        parsed_info_c = parse_c_function(c_code_unopt)
    except (ParsingError, ValueError) as e:
        print(f"Error parsing C code: {e}")
        sys.exit(1)

    # Generate extended driver code
    driver_code = generate_extended_driver(parsed_info_c, unopt_rise_code, c_file_unopt, 
                                         dimension, precision, float_type, iterations,
                                         include_negatives, metrics_file_path, parsed_rise)

    # Apply prefix to output file name if provided
    if prefix and not output_file_name.startswith(prefix):
        output_file_name = f"{prefix}{output_file_name}"

    # Write the driver code to a file in the out directory
    output_file = os.path.join(out_dir, output_file_name)

    with open(output_file, "w") as f:
        f.write(driver_code)

    print(f"Successfully generated {output_file}")

    # Compile the comparison driver with gcc
    try:
        # Apply prefix to executable name if provided
        executable_name = os.path.join(out_dir, os.path.splitext(output_file_name)[0])
        cmd = ["gcc", "-o", executable_name, output_file, c_file_unopt, c_file_mpfr_unopt, c_file_opt, "-lm", "-lmpfr", "-fopenmp"]
        print(f"Compilation command: {' '.join(cmd)}")
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
