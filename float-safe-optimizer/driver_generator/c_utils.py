from typing import List
def sign_code(include_negatives: bool) -> str:
    return """
    // Randomly negate values
    if (rand() % 2) {
      val = -val;
    }""" if include_negatives else ""

headers = """
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <mpfr.h>
#include <float.h>
#include <string.h>
"""

get_time_func = """
double get_time_in_seconds() {{
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return ts.tv_sec + ts.tv_nsec * 1e-9;
}}
"""

def generate_extern_functions(base_name: str, dimensions: List[str], inputs: List[str], param_types: List[str] = None) -> str:
    """Generate extern function declarations with correct types."""
    output_type = param_types[0] if param_types else "float*"
    
    # Create input parameters based on actual types
    input_params = []
    input_params_mpfr = []
    
    for i in range(len(inputs)):
        input_type = param_types[i+len(dimensions)+1] if param_types else "float*"
        input_params.append(f"{input_type} x{i}")
        input_params_mpfr.append(f"mpfr_t *x{i}_mpfr")
    
    return f"""
extern void {base_name}_unopt({output_type} output, {', '.join([f"int {dim}" for dim in dimensions])}, {', '.join(input_params)});
extern void {base_name}_opt({output_type} output, {', '.join([f"int {dim}" for dim in dimensions])}, {', '.join(input_params)});
extern void {base_name}_mpfr(mpfr_t *output, {', '.join([f"int {dim}" for dim in dimensions])}, {', '.join(input_params_mpfr)});
"""