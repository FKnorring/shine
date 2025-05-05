from typing import List, Dict, Any, Tuple

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

def generate_cleanup_code(parsed_rise: Dict[str, Any], input_config: Dict[str, Any] = None) -> str:
    """Generate cleanup code for freeing memory and clearing MPFR variables.
    
    Args:
        parsed_rise: Parsed RISE information
        input_config: Input configuration dictionary
        
    Returns:
        str: Generated cleanup code
    """
    input_sizes, output_size = calculate_array_sizes(parsed_rise, input_config)
    
    # Generate cleanup for input arrays
    input_cleanup = []
    for i, size in enumerate(input_sizes):
        input_cleanup.append(f"""
  // Clean up input {i}
  for (int j = 0; j < {size}; j++) {{
    mpfr_clear(x{i}_mpfr[j]);
  }}
  free(x{i});
  free(x{i}_mpfr);""")
    
    return f"""
  // Clean up input arrays
{''.join(input_cleanup)}

  // Clean up output arrays
  for (int i = 0; i < {output_size}; i++) {{
    mpfr_clear(output_mpfr[i]);
  }}
  free(output_unopt);
  free(output_opt);
  free(output_mpfr);
  
  // Free arrays used for tracking times and results
  free(unopt_times);
  free(opt_times);
  free(opt_results);
  free(sorted_unopt_times);
  free(sorted_opt_times);
  free(sorted_opt_results);
  
  // Clear temporary MPFR variables
  mpfr_clear(unopt_mpfr_temp);
  mpfr_clear(opt_mpfr_temp);
  mpfr_clear(mpfr_diff_unopt_temp);
  mpfr_clear(mpfr_diff_opt_temp);
""" 