from typing import Dict, List, Any
from parser import ParsingError

def generate_includes_and_helpers() -> List[str]:
    """Generate the include statements and helper functions."""
    return [
        "#include <stdio.h>",
        "#include <stdlib.h>",
        "#include <time.h>",
        "#include <math.h>",
        "#include <mpfr.h>",
        "",
        "double get_time_in_seconds() {",
        "  struct timespec ts;",
        "  clock_gettime(CLOCK_MONOTONIC, &ts);",
        "  return ts.tv_sec + ts.tv_nsec * 1e-9;",
        "}",
        ""
    ]

def generate_extern_functions(parsed_info: Dict[str, Any]) -> List[str]:
    """Generate extern declarations for both standard and MPFR versions."""
    lines = []
    
    # Standard version
    params = []
    params.append(f"{parsed_info['output']['type']} {parsed_info['output']['name']}")
    for dim in parsed_info['dimensions']:
        params.append(f"{dim['type']} {dim['name']}")
    for inp in parsed_info['inputs']:
        params.append(f"{inp['type']} {inp['name']}")
    lines.append(f"extern void {parsed_info['name']}({', '.join(params)});")
    
    # MPFR version
    mpfr_params = []
    mpfr_params.append(f"mpfr_t *{parsed_info['output']['name']}")
    for dim in parsed_info['dimensions']:
        mpfr_params.append(f"{dim['type']} {dim['name']}")
    for inp in parsed_info['inputs']:
        mpfr_params.append(f"mpfr_t *{inp['name']}")
    lines.append(f"extern void {parsed_info['name']}_mpfr({', '.join(mpfr_params)});")
    
    return lines

def get_array_size(parsed_info: Dict[str, Any], array_name: str) -> str:
    """Get the size expression for an array based on its dimensions."""
    dims = [d["name"] for d in parsed_info["dimensions"]]
    
    # For sum.rise, we only have one dimension
    if len(dims) == 1:
        return dims[0]
    
    # For matrix multiplication, we have three dimensions
    if len(dims) == 3:
        if array_name == parsed_info["output"]["name"]:
            return f"{dims[0]} * {dims[1]}"  # output is n0 * n1
        elif array_name == parsed_info["inputs"][0]["name"]:
            return f"{dims[0]} * {dims[2]}"  # first input is n0 * n2
        elif array_name == parsed_info["inputs"][1]["name"]:
            return f"{dims[1]} * {dims[2]}"  # second input is n1 * n2
    
    # Default case (should not happen)
    return " * ".join(dims)

def generate_array_allocations(parsed_info: Dict[str, Any]) -> List[str]:
    """Generate code for array allocations for both standard and MPFR versions."""
    lines = []
    
    # Standard version allocations
    output_size = get_array_size(parsed_info, parsed_info["output"]["name"])
    lines.append(f"  {parsed_info['output']['type']} {parsed_info['output']['name']} = "
                f"malloc({output_size} * sizeof(float));")
    
    for inp in parsed_info['inputs']:
        input_size = get_array_size(parsed_info, inp["name"])
        lines.append(f"  {inp['type']} {inp['name']} = "
                    f"malloc({input_size} * sizeof(float));")
    
    # MPFR version allocations
    lines.append(f"  mpfr_t *{parsed_info['output']['name']}_mpfr = "
                f"malloc({output_size} * sizeof(mpfr_t));")
    
    for inp in parsed_info['inputs']:
        input_size = get_array_size(parsed_info, inp["name"])
        lines.append(f"  mpfr_t *{inp['name']}_mpfr = "
                    f"malloc({input_size} * sizeof(mpfr_t));")
    
    return lines

def generate_array_initialization(parsed_info: Dict[str, Any], precision: int = 256, float_type: str = "normal") -> List[str]:
    """Generate code for initializing arrays with random data for both versions.
    
    Args:
        parsed_info: The parsed function information
        precision: The MPFR precision in bits
        float_type: Type of floating point numbers to generate:
            - normal: Regular random numbers between 0 and 1
            - subnormal: Denormalized/subnormal floating point numbers
            - mixed: A mixture of normal and subnormal numbers
            - magnitude: A mixture of high and low magnitude numbers
    """
    lines = []
    
    # Add helper function for generating different types of floats
    if float_type != "normal":
        lines.extend([
            "  // Helper function to generate different types of floating point numbers",
            "  float generate_float(int type, int idx) {",
            "    float val = (float)rand() / RAND_MAX;",
            "    ",
            "    switch(type) {",
            "      case 1: // subnormal",
            "        // Generate a subnormal float (between 0 and 2^-126 ≈ 1.18e-38)",
            "        return val * 1.18e-38f;",
            "      case 2: // mixed (normal and subnormal)",
            "        // 50% chance of generating a subnormal number",
            "        if (rand() % 2 == 0) {",
            "          return val * 1.18e-38f;",
            "        } else {",
            "          return val;",
            "        }",
            "      case 3: // magnitude (high and low)",
            "        // Generate numbers with varying magnitudes",
            "        // 33% small, 33% medium, 33% large",
            "        int choice = rand() % 3;",
            "        if (choice == 0) {",
            "          return val * 1.0e-20f; // Small but not subnormal",
            "        } else if (choice == 1) {",
            "          return val; // Medium",
            "        } else {",
            "          return val * 1.0e20f; // Large",
            "        }",
            "      default:",
            "        return val;",
            "    }",
            "  }",
            ""
        ])
    
    # Initialize standard version
    for inp in parsed_info['inputs']:
        input_size = get_array_size(parsed_info, inp["name"])
        lines.append(f"  for (int i = 0; i < {input_size}; i++) {{")
        
        # Generate floating point values based on the requested type
        if float_type == "normal":
            lines.append(f"    float val = (float)rand() / RAND_MAX;")
        elif float_type == "subnormal":
            lines.append(f"    float val = generate_float(1, i);")
        elif float_type == "mixed":
            lines.append(f"    float val = generate_float(2, i);")
        elif float_type == "magnitude":
            lines.append(f"    float val = generate_float(3, i);")
        
        lines.extend([
            f"    {inp['name']}[i] = val;",
            f"    mpfr_init2({inp['name']}_mpfr[i], {precision});",
            f"    mpfr_set_d({inp['name']}_mpfr[i], val, MPFR_RNDN);",
            "  }"
        ])
    
    # Initialize MPFR output arrays
    output_size = get_array_size(parsed_info, parsed_info["output"]["name"])
    lines.extend([
        f"  for (int i = 0; i < {output_size}; i++) {{",
        f"    mpfr_init2({parsed_info['output']['name']}_mpfr[i], {precision});",
        "  }"
    ])
    
    return lines

def generate_benchmark_code(parsed_info: Dict[str, Any]) -> List[str]:
    """Generate the benchmarking code for both versions."""
    lines = []
    
    # Standard version benchmark
    args_standard = [parsed_info["output"]["name"]] + [dim["name"] for dim in parsed_info["dimensions"]] + [inp["name"] for inp in parsed_info["inputs"]]
    lines.extend([
        "  // Standard version benchmark",
        "  int iterations = 50;",
        "  double start_time = get_time_in_seconds();",
        "  for (int iter = 0; iter < iterations; iter++) {",
        f"    {parsed_info['name']}({', '.join(args_standard)});",
        "  }",
        "  double end_time = get_time_in_seconds();",
        "  double standard_time = (end_time - start_time) / iterations;",
        "  printf(\"Standard version: %f seconds per iteration\\n\", standard_time);",
        ""
    ])
    
    # MPFR version benchmark
    args_mpfr = [f"{parsed_info['output']['name']}_mpfr"] + [dim["name"] for dim in parsed_info["dimensions"]] + [f"{inp['name']}_mpfr" for inp in parsed_info["inputs"]]
    lines.extend([
        "  // MPFR version benchmark",
        "  start_time = get_time_in_seconds();",
        "  for (int iter = 0; iter < iterations; iter++) {",
        f"    {parsed_info['name']}_mpfr({', '.join(args_mpfr)});",
        "  }",
        "  end_time = get_time_in_seconds();",
        "  double mpfr_time = (end_time - start_time) / iterations;",
        "  printf(\"MPFR version: %f seconds per iteration\\n\", mpfr_time);",
        ""
    ])
    
    # Accuracy comparison using MPFR
    output_size = get_array_size(parsed_info, parsed_info["output"]["name"])
    lines.extend([
        "  // Accuracy comparison",
        "  mpfr_t max_diff, avg_diff, diff, temp;",
        "  mpfr_init2(max_diff, 256);",
        "  mpfr_init2(avg_diff, 256);",
        "  mpfr_init2(diff, 256);",
        "  mpfr_init2(temp, 256);",
        "  ",
        "  mpfr_set_d(max_diff, 0.0, MPFR_RNDN);",
        "  mpfr_set_d(avg_diff, 0.0, MPFR_RNDN);",
        "  ",
        f"  for (int i = 0; i < {output_size}; i++) {{",
        "    // Convert float output to mpfr",
        f"    mpfr_set_d(temp, {parsed_info['output']['name']}[i], MPFR_RNDN);",
        "    // Calculate |output_mpfr[i] - temp|",
        f"    mpfr_sub(diff, {parsed_info['output']['name']}_mpfr[i], temp, MPFR_RNDN);",
        "    mpfr_abs(diff, diff, MPFR_RNDN);",
        "    ",
        "    // Update max_diff",
        "    if (mpfr_cmp(diff, max_diff) > 0) {",
        "      mpfr_set(max_diff, diff, MPFR_RNDN);",
        "    }",
        "    ",
        "    // Update avg_diff",
        "    mpfr_add(avg_diff, avg_diff, diff, MPFR_RNDN);",
        "  }",
        "  ",
        "  // Calculate average",
        f"  mpfr_div_ui(avg_diff, avg_diff, {output_size}, MPFR_RNDN);",
        "  ",
        "  printf(\"\\nAccuracy Comparison:\\n\");",
        "  printf(\"  Maximum absolute error: %e\\n\", mpfr_get_d(max_diff, MPFR_RNDN));",
        "  printf(\"  Average absolute error: %e\\n\", mpfr_get_d(avg_diff, MPFR_RNDN));",
        "  printf(\"\\nMPFR Slowdown: %.2fx\\n\", mpfr_time / standard_time);",
        ""
    ])
    
    return lines

def generate_cleanup_code(parsed_info: Dict[str, Any]) -> List[str]:
    """Generate memory cleanup code for both versions."""
    lines = []
    
    # Free standard version arrays
    lines.append(f"  free({parsed_info['output']['name']});")
    for inp in parsed_info['inputs']:
        lines.append(f"  free({inp['name']});")
    
    # Free MPFR version arrays
    output_size = get_array_size(parsed_info, parsed_info["output"]["name"])
    lines.append(f"  for (int i = 0; i < {output_size}; i++) {{")
    lines.append(f"    mpfr_clear({parsed_info['output']['name']}_mpfr[i]);")
    lines.append("  }")
    
    for inp in parsed_info['inputs']:
        input_size = get_array_size(parsed_info, inp["name"])
        lines.append(f"  for (int i = 0; i < {input_size}; i++) {{")
        lines.append(f"    mpfr_clear({inp['name']}_mpfr[i]);")
        lines.append("  }")
    
    lines.append(f"  free({parsed_info['output']['name']}_mpfr);")
    for inp in parsed_info['inputs']:
        lines.append(f"  free({inp['name']}_mpfr);")
    
    # Clear MPFR variables used for error calculation
    lines.append("  ")
    lines.append("  // Clear MPFR variables used for error calculation")
    lines.append("  mpfr_clear(max_diff);")
    lines.append("  mpfr_clear(avg_diff);")
    lines.append("  mpfr_clear(diff);")
    lines.append("  mpfr_clear(temp);")
    
    return lines

def generate_driver(parsed_info: Dict[str, Any], rise_code: str = None, dimension: int = 256, precision: int = 256, float_type: str = "normal") -> str:
    """Generate the complete comparison driver code.
    
    Args:
        parsed_info: The parsed function information
        rise_code: The RISE source code
        dimension: The dimension size for all dimensions
        precision: The MPFR precision in bits
        float_type: Type of floating point numbers to generate:
            - normal: Regular random numbers between 0 and 1
            - subnormal: Denormalized/subnormal floating point numbers
            - mixed: A mixture of normal and subnormal numbers
            - magnitude: A mixture of high and low magnitude numbers
    """
    driver_lines = []
    
    # Add includes and helper functions
    driver_lines.extend(generate_includes_and_helpers())
    
    # Add extern function declarations
    driver_lines.extend(generate_extern_functions(parsed_info))
    driver_lines.append("")
    
    # Begin main function
    driver_lines.append("int main(int argc, char** argv) {")
    
    # Add dimension declarations
    driver_lines.append("  // Set dimensions")
    for dim in parsed_info["dimensions"]:
        driver_lines.append(f"  int {dim['name']} = {dimension}; // dimension size for {dim['name']}")
    driver_lines.append("")
    
    # Add array allocations
    driver_lines.extend(generate_array_allocations(parsed_info))
    driver_lines.append("")
    
    # Add allocation check
    check_vars = [parsed_info['output']['name']] + [inp['name'] for inp in parsed_info["inputs"]] + \
                 [f"{parsed_info['output']['name']}_mpfr"] + [f"{inp['name']}_mpfr" for inp in parsed_info["inputs"]]
    driver_lines.append("  if (!" + " || !".join(check_vars) + ") {")
    driver_lines.append("    fprintf(stderr, \"Allocation failed.\\n\");")
    driver_lines.append("    return EXIT_FAILURE;")
    driver_lines.append("  }")
    driver_lines.append("")
    
    # Add array initialization with precision and float type
    driver_lines.extend(generate_array_initialization(parsed_info, precision, float_type))
    driver_lines.append("")
    
    # Add benchmark code
    driver_lines.extend(generate_benchmark_code(parsed_info))
    
    # Add cleanup code
    driver_lines.extend(generate_cleanup_code(parsed_info))
    driver_lines.append("")
    
    # Add return statement
    driver_lines.append("  return EXIT_SUCCESS;")
    driver_lines.append("}")
    
    return "\n".join(driver_lines) 