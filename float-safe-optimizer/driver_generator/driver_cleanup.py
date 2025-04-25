from typing import List

def generate_cleanup_code(dimensions: List[int]) -> str:
    """Generate cleanup code for freeing memory and clearing MPFR variables.
    
    Args:
        dimensions: List of array dimensions
        
    Returns:
        str: Generated cleanup code
    """
    return f"""
  // Free memory and clean up
  free(output_unopt);
  free(output_opt);
  free(x0);
  mpfr_clear(output_mpfr[0]);
  for (int i = 0; i < {' * '.join([f"{dim}" for dim in dimensions])}; i++) {{
    mpfr_clear(x0_mpfr[i]);
  }}
  free(output_mpfr);
  free(x0_mpfr);
  
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