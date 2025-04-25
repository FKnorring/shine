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

def generate_extern_functions(base_name: str, dimensions: List[str], inputs: List[str]) -> str:
    """Generate extern function declarations."""
    input_params = ', '.join([f"float* x{i}" for i in range(len(inputs))])
    input_params_mpfr = ', '.join([f"mpfr_t *x{i}_mpfr" for i in range(len(inputs))])
    return f"""
extern void {base_name}_unopt(float* output, {', '.join([f"int {dim}" for dim in dimensions])}, {input_params});
extern void {base_name}_opt(float* output, {', '.join([f"int {dim}" for dim in dimensions])}, {input_params});
extern void {base_name}_mpfr(mpfr_t *output, {', '.join([f"int {dim}" for dim in dimensions])}, {input_params_mpfr});
"""