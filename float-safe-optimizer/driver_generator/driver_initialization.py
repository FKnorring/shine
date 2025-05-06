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

def allocate_input_arrays(parsed_rise: Dict[str, Any], input_config: Dict[str, Any] = None, param_types: List[str] = None) -> Tuple[str, List[int]]:
    input_allocs = []
    input_sizes, _ = calculate_array_sizes(parsed_rise, input_config)
    
    for i, size in enumerate(input_sizes):
        # Determine the correct type (float or double)
        array_type = "double" if param_types and "double*" in param_types[i+len(parsed_rise["dimensions"])+1] else "float"
        
        input_allocs.append(f"""
  {array_type}* x{i} = malloc({size} * sizeof({array_type}));
  mpfr_t *x{i}_mpfr = malloc({size} * sizeof(mpfr_t));""")
    
    return "\n".join(input_allocs), input_sizes

def allocate_output_arrays(parsed_rise: Dict[str, Any], input_config: Dict[str, Any] = None, param_types: List[str] = None) -> str:
    _, output_size = calculate_array_sizes(parsed_rise, input_config)
    output_type = "double" if param_types and "double" in param_types[0] else "float"
    
    return f"""
  {output_type}* output_unopt = malloc({output_size} * sizeof({output_type}));
  {output_type}* output_opt = malloc({output_size} * sizeof({output_type}));
  mpfr_t *output_mpfr = malloc({output_size} * sizeof(mpfr_t));"""

def allocate_metric_arrays(iterations: int, result_type: str = "float") -> str:
    return f"""
  // Arrays to track performance times for each iteration
  double* unopt_times = malloc({iterations} * sizeof(double));
  {result_type}* unopt_results = malloc({iterations} * sizeof({result_type}));
  double* opt_times = malloc({iterations} * sizeof(double));
  {result_type}* opt_results = malloc({iterations} * sizeof({result_type}));
  
  // Arrays for sorted results
  double* sorted_unopt_times = malloc({iterations} * sizeof(double));
  double* sorted_opt_times = malloc({iterations} * sizeof(double));
  {result_type}* sorted_opt_results = malloc({iterations} * sizeof({result_type}));"""

def check_allocations(num_inputs: int) -> str:
    input_checks = " || ".join([f"!x{i} || !x{i}_mpfr" for i in range(num_inputs)])
    return f"""
  if (!output_unopt || !output_opt || !output_mpfr || {input_checks} || 
      !unopt_times || !opt_times || !opt_results ||
      !sorted_unopt_times || !sorted_opt_times || !sorted_opt_results) {{
    fprintf(stderr, "Allocation failed.\\n");
    return EXIT_FAILURE;
  }}"""

def initialize_input_arrays(parsed_rise: Dict[str, Any], precision: int, float_type: str, include_negatives: bool, input_config: Dict[str, Any] = None, param_types: List[str] = None) -> str:
    input_inits = []
    input_sizes, _ = calculate_array_sizes(parsed_rise, input_config)
    
    for i, size in enumerate(input_sizes):
        # Get the correct C type (float or double)
        c_type = "double" if param_types and "double" in param_types[i+len(parsed_rise["dimensions"])+1] else "float"
        
        # Initialize MPFR variables first
        input_inits.append(f"""
  // Initialize MPFR variables for input {i}
  for (int j = 0; j < {size}; j++) {{
    mpfr_init2(x{i}_mpfr[j], {precision});
  }}""")
        
        # Create initialization code that respects float_type (distribution) and include_negatives
        neg_code = "if (rand() % 2) {\n      val = -val;\n    }" if include_negatives else ""
        
        # Type-specific initialization logic based on float_type parameter
        init_code = ""
        if float_type == "normal":
            init_code = f"""
    {c_type} val;
    val = ({c_type})rand() / RAND_MAX;
    {neg_code}"""
        elif float_type == "subnormal":
            init_code = f"""
    {c_type} val;
    val = ({c_type})((rand() % 1000) * 1e-45);
    {neg_code}"""
        elif float_type == "mixed":
            init_code = f"""
    {c_type} val;
    if (rand() % 2) {{
      val = ({c_type})rand() / RAND_MAX;
    }} else {{
      val = ({c_type})((rand() % 1000) * 1e-45);
    }}
    {neg_code}"""
        elif float_type == "magnitude":
            init_code = f"""
    {c_type} val;
    if (rand() % 2) {{
      val = ({c_type})(rand() * 1e10);
    }} else {{
      val = ({c_type})(rand() * 1e-10);
    }}
    {neg_code}"""
        
        # Then initialize values
        input_inits.append(f"""
  // Initialize values for input {i}
  for (int j = 0; j < {size}; j++) {{{init_code}
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

def generate_initialization_code(dimensions: List[str], dimension: int, iterations: int, precision: int, float_type: str, include_negatives: bool, parsed_rise: Dict[str, Any], input_config: Dict[str, Any] = None, param_types: List[str] = None) -> str:
    """Generate initialization code for the driver."""
    
    # Get the result type for metrics arrays
    result_type = "double" if param_types and "double*" in param_types[0] else "float"

    print("RESULT TYPE: ", result_type)
    print("PARAM TYPES: ", param_types)
    
    # Generate all initialization components with input config
    dim_decls = declare_dimension_sizes(dimensions, dimension, input_config)
    input_allocs, input_sizes = allocate_input_arrays(parsed_rise, input_config, param_types)
    output_allocs = allocate_output_arrays(parsed_rise, input_config, param_types)
    metric_allocs = allocate_metric_arrays(iterations, result_type)
    alloc_checks = check_allocations(len(parsed_rise["inputs"]))
    input_inits = initialize_input_arrays(parsed_rise, precision, float_type, include_negatives, input_config, param_types)
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