from typing import List, Tuple, Dict, Any
from floating_point_generation import get_float_value

def declare_dimension_sizes(dimensions: List[str], dimension: int, input_config: Dict[str, Any] = None) -> str:
    # If input config is provided, use dimension sizes from it
    if input_config and "dimensions" in input_config:
        dimension_decls = []
        for dim in dimensions:
            # Use the provided dimension size if available, otherwise use default
            dim_size = input_config["dimensions"].get(dim, dimension)
            dimension_decls.append(f"int {dim} = {dim_size};")
        return f"""
  // Set dimensions
  {' '.join(dimension_decls)}"""
    else:
        # Default behavior: use the same dimension for all
        dimension_decls = '  '.join([f"int {dim} = {dimension};" for dim in dimensions])
        return f"""
  // Set dimensions
  {dimension_decls}"""

def calculate_array_sizes(parsed_rise: Dict[str, Any], input_config: Dict[str, Any] = None) -> Tuple[List[int], int]:
    """Calculate sizes for input and output arrays based on dimensions."""
    input_sizes = []
    output_size = 1
    
    # Calculate output size
    if "output" in parsed_rise:
        output_size = 1
        for dim in parsed_rise["output"].split(' * '):
            if input_config and "dimensions" in input_config and dim in input_config["dimensions"]:
                output_size *= input_config["dimensions"][dim]
            else:
                output_size *= 1  # Default to 1 if dimension not found
    
    # Calculate input sizes
    for input_size in parsed_rise["inputs"]:
        size = 1
        for dim in input_size.split(' * '):
            if input_config and "dimensions" in input_config and dim in input_config["dimensions"]:
                size *= input_config["dimensions"][dim]
            else:
                size *= 1  # Default to 1 if dimension not found
        input_sizes.append(size)
    
    return input_sizes, output_size

def allocate_input_arrays(parsed_rise: Dict[str, Any], input_config: Dict[str, Any] = None) -> Tuple[str, List[int]]:
    input_allocs = []
    input_sizes, _ = calculate_array_sizes(parsed_rise, input_config)
    
    for i, size in enumerate(input_sizes):
        input_allocs.append(f"""
  float* x{i} = malloc({size} * sizeof(float));
  mpfr_t *x{i}_mpfr = malloc({size} * sizeof(mpfr_t));""")
    
    return "\n".join(input_allocs), input_sizes

def allocate_output_arrays(parsed_rise: Dict[str, Any], input_config: Dict[str, Any] = None) -> str:
    _, output_size = calculate_array_sizes(parsed_rise, input_config)
    return f"""
  float* output_unopt = malloc({output_size} * sizeof(float));
  float* output_opt = malloc({output_size} * sizeof(float));
  mpfr_t *output_mpfr = malloc({output_size} * sizeof(mpfr_t));"""

def allocate_metric_arrays(iterations: int) -> str:
    return f"""
  // Arrays to track performance times for each iteration
  double* unopt_times = malloc({iterations} * sizeof(double));
  double* opt_times = malloc({iterations} * sizeof(double));
  float* opt_results = malloc({iterations} * sizeof(float));
  
  // Arrays for sorted results
  double* sorted_unopt_times = malloc({iterations} * sizeof(double));
  double* sorted_opt_times = malloc({iterations} * sizeof(double));
  float* sorted_opt_results = malloc({iterations} * sizeof(float));"""

def check_allocations(num_inputs: int) -> str:
    input_checks = " || ".join([f"!x{i} || !x{i}_mpfr" for i in range(num_inputs)])
    return f"""
  if (!output_unopt || !output_opt || !output_mpfr || {input_checks} || 
      !unopt_times || !opt_times || !opt_results ||
      !sorted_unopt_times || !sorted_opt_times || !sorted_opt_results) {{
    fprintf(stderr, "Allocation failed.\\n");
    return EXIT_FAILURE;
  }}"""

def initialize_input_arrays(parsed_rise: Dict[str, Any], precision: int, float_type: str, include_negatives: bool, input_config: Dict[str, Any] = None) -> str:
    input_inits = []
    input_sizes, _ = calculate_array_sizes(parsed_rise, input_config)
    
    for i, size in enumerate(input_sizes):
        # Initialize MPFR variables first
        input_inits.append(f"""
  // Initialize MPFR variables for input {i}
  for (int j = 0; j < {size}; j++) {{
    mpfr_init2(x{i}_mpfr[j], {precision});
  }}""")
        
        # Then initialize values
        input_inits.append(f"""
  // Initialize values for input {i}
  for (int j = 0; j < {size}; j++) {{
    float val;
    if (rand() % 2) {{
      val = (float)rand() / RAND_MAX;
    }} else {{
      val = (float)((rand() % 1000) * 1e-45);
    }}
    if (rand() % 2) {{
      val = -val;
    }}
    x{i}[j] = val;
    mpfr_set_d(x{i}_mpfr[j], val, MPFR_RNDN);
  }}""")
    
    return "\n".join(input_inits)

def initialize_output_arrays(parsed_rise: Dict[str, Any], precision: int, input_config: Dict[str, Any] = None) -> str:
    _, output_size = calculate_array_sizes(parsed_rise, input_config)
    return f"""
  // Initialize output arrays
  for (int i = 0; i < {output_size}; i++) {{
    mpfr_init2(output_mpfr[i], {precision});
  }}"""

def generate_initialization_code(dimensions: List[str], dimension: int, iterations: int, precision: int, float_type: str, include_negatives: bool, parsed_rise: Dict[str, Any], input_config: Dict[str, Any] = None) -> str:
    """Generate initialization code for the driver."""
    
    # Generate all initialization components with input config
    dim_decls = declare_dimension_sizes(dimensions, dimension, input_config)
    input_allocs, input_sizes = allocate_input_arrays(parsed_rise, input_config)
    output_allocs = allocate_output_arrays(parsed_rise, input_config)
    metric_allocs = allocate_metric_arrays(iterations)
    alloc_checks = check_allocations(len(parsed_rise["inputs"]))
    input_inits = initialize_input_arrays(parsed_rise, precision, float_type, include_negatives, input_config)
    output_inits = initialize_output_arrays(parsed_rise, precision, input_config)
    
    # Combine all components
    return f"""
{dim_decls}

  // Set iterations count
  int iterations = {iterations};
{input_allocs}
{output_allocs}
{metric_allocs}
{alloc_checks}
{input_inits}
{output_inits}
""" 