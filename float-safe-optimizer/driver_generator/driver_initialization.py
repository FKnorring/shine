from typing import List, Tuple, Dict, Any
from floating_point_generation import get_float_value

def declare_dimension_sizes(dimensions: List[str], dimension: int) -> str:
    dimension_decls = '  '.join([f"int {dim} = {dimension};" for dim in dimensions])
    return f"""
  // Set dimensions
  {dimension_decls}"""

def allocate_input_arrays(parsed_rise: Dict[str, Any]) -> Tuple[str, List[str]]:
    input_allocs = []
    array_sizes = []
    
    for i, input_size in enumerate(parsed_rise["inputs"]):
        input_allocs.append(f"""
  float* x{i} = malloc({input_size} * sizeof(float));
  mpfr_t *x{i}_mpfr = malloc({input_size} * sizeof(mpfr_t));""")
        array_sizes.append(input_size)
    
    return "\n".join(input_allocs), array_sizes

def allocate_output_arrays(parsed_rise: Dict[str, Any]) -> str:
    output_size = parsed_rise["output"]
    return f"""
  float* output_unopt = malloc({output_size} * sizeof(float));
  float* output_opt = malloc({output_size} * sizeof(float));
  mpfr_t *output_mpfr = malloc({output_size} * sizeof(mpfr_t));"""

def allocate_metric_arrays(iterations: int) -> str:
    return f"""
  // Arrays to track performance times for each iteration
  double* unopt_times = malloc({iterations} * sizeof(double));
  double* opt_times = malloc({iterations} * sizeof(double));
  
  // Array to track results of the optimized version for each iteration
  float* opt_results = malloc({iterations} * sizeof(float));"""

def check_allocations(num_inputs: int) -> str:
    input_checks = " || ".join([f"!x{i} || !x{i}_mpfr" for i in range(num_inputs)])
    return f"""
  if (!output_unopt || !output_opt || !output_mpfr || {input_checks} || 
      !unopt_times || !opt_times || !opt_results) {{
    fprintf(stderr, "Allocation failed.\\n");
    return EXIT_FAILURE;
  }}"""

def initialize_input_arrays(parsed_rise: Dict[str, Any], precision: int, float_type: str, include_negatives: bool) -> str:
    input_inits = []
    for i, input_size in enumerate(parsed_rise["inputs"]):
        input_inits.append(f"""
  for (int i = 0; i < {input_size}; i++) {{
    {get_float_value(float_type, include_negatives)}
    x{i}[i] = val;
    mpfr_init2(x{i}_mpfr[i], {precision});
    mpfr_set_d(x{i}_mpfr[i], val, MPFR_RNDN);
  }}""")
    return "\n".join(input_inits)

def initialize_output_arrays(parsed_rise: Dict[str, Any], precision: int) -> str:
    output_size = parsed_rise["output"]
    return f"""
  // Initialize output arrays
  for (int i = 0; i < {output_size}; i++) {{
    mpfr_init2(output_mpfr[i], {precision});
  }}"""

def generate_initialization_code(dimensions: List[str], dimension: int, iterations: int, precision: int, float_type: str, include_negatives: bool, parsed_rise: Dict[str, Any]) -> str:
    """Generate initialization code for the driver."""
    # Declare dimension variables
    dimension_decls = '  '.join([f"int {dim} = {dimension};" for dim in dimensions])
    
    # Generate all initialization components
    dim_decls = declare_dimension_sizes(dimensions, dimension)
    input_allocs, array_sizes = allocate_input_arrays(parsed_rise)
    output_allocs = allocate_output_arrays(parsed_rise)
    metric_allocs = allocate_metric_arrays(iterations)
    alloc_checks = check_allocations(len(parsed_rise["inputs"]))
    input_inits = initialize_input_arrays(parsed_rise, precision, float_type, include_negatives)
    output_inits = initialize_output_arrays(parsed_rise, precision)
    
    # Combine all components
    return f"""
{dim_decls}

  // Set random seed for reproducibility
  srand(42);

  // Set iterations count
  int iterations = {iterations};
{input_allocs}
{output_allocs}
{metric_allocs}
{alloc_checks}
{input_inits}
{output_inits}
""" 