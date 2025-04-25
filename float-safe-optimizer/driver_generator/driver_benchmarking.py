from typing import List, Tuple

def run_mpfr_reference(base_name: str, dimensions: List[str], inputs: List[str]) -> str:
    input_params = ', '.join([f'x{i}_mpfr' for i in range(len(inputs))])
    return f"""
  // Run MPFR version once as ground truth
  printf("Running MPFR reference version (ground truth)...\\n");
  {base_name}_mpfr(output_mpfr, {', '.join([f"{dim}" for dim in dimensions])}, {input_params});
  double mpfr_val = mpfr_get_d(output_mpfr[0], MPFR_RNDN);
  printf("MPFR reference result: %e\\n", mpfr_val);"""

def initialize_mpfr_temporaries(precision: int) -> str:
    return f"""
  // Initialize temporary MPFR variables for error calculations
  mpfr_t unopt_mpfr_temp, opt_mpfr_temp, mpfr_diff_unopt_temp, mpfr_diff_opt_temp;
  mpfr_init2(unopt_mpfr_temp, {precision});
  mpfr_init2(opt_mpfr_temp, {precision});
  mpfr_init2(mpfr_diff_unopt_temp, {precision});
  mpfr_init2(mpfr_diff_opt_temp, {precision});"""

def run_benchmark_iterations(base_name: str, dimensions: List[str], inputs: List[str], iterations: int) -> str:
    input_params = ', '.join([f'x{i}' for i in range(len(inputs))])
    return f"""
  // Store unoptimized result for accuracy comparison
  double unopt_first_val;
  
  // Run all implementations for each iteration and track performance and results
  printf("Running %d iterations of benchmarks...\\n", {iterations});
  for (int iter = 0; iter < {iterations}; iter++) {{
    // Run unoptimized version
    double start_time = get_time_in_seconds();
    {base_name}_unopt(output_unopt, {', '.join([f"{dim}" for dim in dimensions])}, {input_params});
    double end_time = get_time_in_seconds();
    unopt_times[iter] = end_time - start_time;
    
    // Save the first unoptimized result for comparison
    if (iter == 0) {{
      unopt_first_val = output_unopt[0];
    }}
    
    // Run optimized version
    start_time = get_time_in_seconds();
    {base_name}_opt(output_opt, {', '.join([f"{dim}" for dim in dimensions])}, {input_params});
    end_time = get_time_in_seconds();
    opt_times[iter] = end_time - start_time;
    
    // Store optimized result for this iteration
    opt_results[iter] = output_opt[0];
  }}"""

def sort_arrays(iterations: int) -> str:
    return f"""
  // Sort the time arrays for calculating median and quantiles
  double* sorted_unopt_times = malloc({iterations} * sizeof(double));
  double* sorted_opt_times = malloc({iterations} * sizeof(double));
  memcpy(sorted_unopt_times, unopt_times, {iterations} * sizeof(double));
  memcpy(sorted_opt_times, opt_times, {iterations} * sizeof(double));
  qsort(sorted_unopt_times, {iterations}, sizeof(double), compare_doubles);
  qsort(sorted_opt_times, {iterations}, sizeof(double), compare_doubles);
  
  // Sort the optimized results for statistical analysis
  float* sorted_opt_results = malloc({iterations} * sizeof(float));
  memcpy(sorted_opt_results, opt_results, {iterations} * sizeof(float));
  qsort(sorted_opt_results, {iterations}, sizeof(float), compare_floats);"""

def calculate_time_statistics(iterations: int) -> str:
    return f"""
  // Calculate mean times
  double unopt_mean_time = 0.0;
  double opt_mean_time = 0.0;
  for (int i = 0; i < {iterations}; i++) {{
    unopt_mean_time += unopt_times[i];
    opt_mean_time += opt_times[i];
  }}
  unopt_mean_time /= {iterations};
  opt_mean_time /= {iterations};
  
  // Calculate median times
  double unopt_median_time = sorted_unopt_times[{iterations} / 2];
  double opt_median_time = sorted_opt_times[{iterations} / 2];
  
  // Calculate variance and std deviation of times
  double unopt_time_variance = variance(unopt_times, {iterations}, unopt_mean_time);
  double opt_time_variance = variance(opt_times, {iterations}, opt_mean_time);
  double unopt_time_stddev = sqrt(unopt_time_variance);
  double opt_time_stddev = sqrt(opt_time_variance);
  
  // Calculate quantiles of times
  double unopt_time_q1 = quantile(sorted_unopt_times, {iterations}, 0.25);
  double unopt_time_q3 = quantile(sorted_unopt_times, {iterations}, 0.75);
  double opt_time_q1 = quantile(sorted_opt_times, {iterations}, 0.25);
  double opt_time_q3 = quantile(sorted_opt_times, {iterations}, 0.75);"""

def calculate_result_statistics(iterations: int) -> str:
    return f"""
  // Calculate mean of optimized results
  double opt_mean_result = 0.0;
  for (int i = 0; i < {iterations}; i++) {{
    opt_mean_result += opt_results[i];
  }}
  opt_mean_result /= {iterations};
  
  // Calculate median of optimized results
  double opt_median_result = sorted_opt_results[{iterations} / 2];
  
  // Calculate variance and std deviation of optimized results
  double opt_result_variance = variance_float(opt_results, {iterations}, opt_mean_result);
  double opt_result_stddev = sqrt(opt_result_variance);
  
  // Calculate quantiles of optimized results
  double opt_result_q1 = quantile_float(sorted_opt_results, {iterations}, 0.25);
  double opt_result_q3 = quantile_float(sorted_opt_results, {iterations}, 0.75);
  
  // Calculate min/max optimized results
  float opt_min_result = sorted_opt_results[0];
  float opt_max_result = sorted_opt_results[{iterations} - 1];"""

def calculate_errors(precision: int) -> str:
    return f"""
  // Convert unoptimized result to MPFR for error calculation
  mpfr_set_d(unopt_mpfr_temp, unopt_first_val, MPFR_RNDN);
  
  // Calculate absolute error for unoptimized result
  mpfr_sub(mpfr_diff_unopt_temp, unopt_mpfr_temp, output_mpfr[0], MPFR_RNDN);
  mpfr_abs(mpfr_diff_unopt_temp, mpfr_diff_unopt_temp, MPFR_RNDN);
  double unopt_error = mpfr_get_d(mpfr_diff_unopt_temp, MPFR_RNDN);
  
  // Calculate relative error for unoptimized result
  double unopt_rel_error = (mpfr_val != 0.0) ? (unopt_error / fabs(mpfr_val)) : 0.0;
  
  // Calculate errors for optimized results (mean)
  mpfr_set_d(opt_mpfr_temp, opt_mean_result, MPFR_RNDN);
  mpfr_sub(mpfr_diff_opt_temp, opt_mpfr_temp, output_mpfr[0], MPFR_RNDN);
  mpfr_abs(mpfr_diff_opt_temp, mpfr_diff_opt_temp, MPFR_RNDN);
  double opt_mean_error = mpfr_get_d(mpfr_diff_opt_temp, MPFR_RNDN);
  double opt_mean_rel_error = (mpfr_val != 0.0) ? (opt_mean_error / fabs(mpfr_val)) : 0.0;"""

def generate_benchmarking_code(base_name: str, dimensions: List[str], inputs: List[str], iterations: int, precision: int) -> str:
    # Generate all benchmarking components
    mpfr_ref = run_mpfr_reference(base_name, dimensions, inputs)
    mpfr_temps = initialize_mpfr_temporaries(precision)
    benchmark_iters = run_benchmark_iterations(base_name, dimensions, inputs, iterations)
    array_sorting = sort_arrays(iterations)
    time_stats = calculate_time_statistics(iterations)
    result_stats = calculate_result_statistics(iterations)
    error_calcs = calculate_errors(precision)
    
    # Combine all components
    return f"""
{mpfr_ref}
{mpfr_temps}
{benchmark_iters}
{array_sorting}
{time_stats}
{result_stats}
{error_calcs}
""" 