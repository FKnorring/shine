from typing import Dict, List, Any
from parser import ParsingError

def generate_includes_and_helpers() -> List[str]:
    """Generate the include statements and helper functions."""
    return [
        "#include <stdio.h>",
        "#include <stdlib.h>",
        "#include <time.h>",
        "",
        "double get_time_in_seconds() {",
        "  struct timespec ts;",
        "  clock_gettime(CLOCK_MONOTONIC, &ts);",
        "  return ts.tv_sec + ts.tv_nsec * 1e-9;",
        "}",
        ""
    ]

def generate_extern_function(parsed_info: Dict[str, Any]) -> List[str]:
    params = []
    params.append(f"{parsed_info['output']['type']} {parsed_info['output']['name']}")

    for dim in parsed_info['dimensions']:
        params.append(f"{dim['type']} {dim['name']}")

    for inp in parsed_info['inputs']:
        params.append(f"{inp['type']} {inp['name']}")
    
    return [f"extern void {parsed_info['name']}({', '.join(params)});"]

def generate_array_allocations(parsed_info: Dict[str, Any], rise_code: str = None) -> List[str]:
    """Generate code for array allocations based on Rise function type if available."""
    lines = []
    
    # For matrix multiplication, we need to allocate:
    # - output: n0 * n1 (result matrix)
    # - x0: n0 * n2 (first input matrix)
    # - x1: n1 * n2 (second input matrix)
    dims = [d["name"] for d in parsed_info["dimensions"]]  # [n0, n1, n2]
    
    # Allocate output array (n0 * n1)
    lines.append(f"  {parsed_info['output']['type']} {parsed_info['output']['name']} = "
                f"malloc({dims[0]} * {dims[1]} * sizeof(float));")
    
    # Allocate first input array (n0 * n2)
    lines.append(f"  {parsed_info['inputs'][0]['type']} {parsed_info['inputs'][0]['name']} = "
                f"malloc({dims[0]} * {dims[2]} * sizeof(float));")
    
    # Allocate second input array (n1 * n2)
    lines.append(f"  {parsed_info['inputs'][1]['type']} {parsed_info['inputs'][1]['name']} = "
                f"malloc({dims[1]} * {dims[2]} * sizeof(float));")
    
    return lines

def generate_array_initialization(parsed_info: Dict[str, Any], rise_code: str = None) -> List[str]:
    """Generate code for initializing arrays with random data."""
    lines = []
    dims = [d["name"] for d in parsed_info["dimensions"]]  # [n0, n1, n2]
    
    # Initialize first input array (n0 * n2)
    lines.extend([
        f"  for (int i = 0; i < {dims[0]} * {dims[2]}; i++) {{",
        f"    {parsed_info['inputs'][0]['name']}[i] = (float)rand() / RAND_MAX;",
        "  }"
    ])
    
    # Initialize second input array (n1 * n2)
    lines.extend([
        f"  for (int i = 0; i < {dims[1]} * {dims[2]}; i++) {{",
        f"    {parsed_info['inputs'][1]['name']}[i] = (float)rand() / RAND_MAX;",
        "  }"
    ])
    
    return lines

def generate_benchmark_code(parsed_info: Dict[str, Any]) -> List[str]:
    """Generate the benchmarking code."""
    args_call = ", ".join(
        [parsed_info["output"]["name"]] +
        [dim["name"] for dim in parsed_info["dimensions"]] +
        [inp["name"] for inp in parsed_info["inputs"]]
    )
    
    return [
        f"  // Warm up call",
        f"  {parsed_info['name']}({args_call});",
        "",
        "  int iterations = 50;",
        "  double start_time = get_time_in_seconds();",
        "  for (int iter = 0; iter < iterations; iter++) {",
        f"    {parsed_info['name']}({args_call});",
        "  }",
        "  double end_time = get_time_in_seconds();",
        "  double total_time = end_time - start_time;",
        "  double average_time = total_time / iterations;",
        "",
        "  printf(\"Total execution time over %d iterations: %f seconds\\n\", iterations, total_time);",
        "  printf(\"Average execution time: %f seconds per call\\n\", average_time);",
        ""
    ]

def generate_cleanup_code(parsed_info: Dict[str, Any]) -> List[str]:
    """Generate memory cleanup code."""
    lines = []
    lines.append(f"  free({parsed_info['output']['name']});")
    for inp in parsed_info["inputs"]:
        lines.append(f"  free({inp['name']});")
    return lines

def generate_driver(parsed_info: Dict[str, Any], rise_code: str = None) -> str:
    """Generate the complete driver code."""
    driver_lines = []
    
    # Add includes and helper functions
    driver_lines.extend(generate_includes_and_helpers())

    # Add extern function declaration
    driver_lines.extend(generate_extern_function(parsed_info))
    driver_lines.append("")
    
    # Begin main function
    driver_lines.append("int main(int argc, char** argv) {")
    
    # Add dimension declarations
    driver_lines.append("  // Set default dimensions")
    for dim in parsed_info["dimensions"]:
        driver_lines.append(f"  int {dim['name']} = 256; // default value for {dim['name']}")
    driver_lines.append("")
    
    # Add array allocations
    driver_lines.extend(generate_array_allocations(parsed_info, rise_code))
    driver_lines.append("")
    
    # Add allocation check with all arrays that were just allocated
    check_vars = [parsed_info['output']['name']] + [inp['name'] for inp in parsed_info["inputs"]]
    driver_lines.append("  if (!" + " || !".join(check_vars) + ") {")
    driver_lines.append("    fprintf(stderr, \"Allocation failed.\\n\");")
    driver_lines.append("    return EXIT_FAILURE;")
    driver_lines.append("  }")
    driver_lines.append("")
    
    # Add array initialization
    driver_lines.extend(generate_array_initialization(parsed_info, rise_code))
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