from typing import List, Tuple

def write_main_metrics_header(metrics_file: str) -> str:
    return f"""
  // Create main metrics file
  FILE *metrics_file_ptr = fopen("{metrics_file}", "w");
  if (!metrics_file_ptr) {{
    fprintf(stderr, "Error: Could not open metrics file for writing\\n");
  }} else {{
    // Write CSV header
    fprintf(metrics_file_ptr, "metric,value,description\\n");"""

def write_configuration_metrics(dimension: int, float_type: str, include_negatives: bool, precision: int) -> str:
    return f"""
    // Write configuration parameters
    fprintf(metrics_file_ptr, "dimension,%d,Array dimension size\\n", {dimension});
    fprintf(metrics_file_ptr, "float_type,%s,Type of floating point values\\n", "{float_type}");
    fprintf(metrics_file_ptr, "include_negatives,%s,Whether negative values were included\\n", "{str(include_negatives).lower()}");
    fprintf(metrics_file_ptr, "precision,%d,MPFR precision bits\\n", {precision});
    fprintf(metrics_file_ptr, "iterations,%d,Number of benchmark iterations\\n", iterations);"""

def write_performance_metrics() -> str:
    return """
    // Write performance metrics - unoptimized
    fprintf(metrics_file_ptr, "unopt_mean_time,%.9f,Unoptimized mean execution time (seconds)\\n", unopt_mean_time);
    fprintf(metrics_file_ptr, "unopt_median_time,%.9f,Unoptimized median execution time (seconds)\\n", unopt_median_time);
    fprintf(metrics_file_ptr, "unopt_min_time,%.9f,Unoptimized minimum execution time (seconds)\\n", sorted_unopt_times[0]);
    fprintf(metrics_file_ptr, "unopt_max_time,%.9f,Unoptimized maximum execution time (seconds)\\n", sorted_unopt_times[iterations - 1]);
    fprintf(metrics_file_ptr, "unopt_time_variance,%.9e,Unoptimized execution time variance\\n", unopt_time_variance);
    fprintf(metrics_file_ptr, "unopt_time_stddev,%.9e,Unoptimized execution time standard deviation\\n", unopt_time_stddev);
    fprintf(metrics_file_ptr, "unopt_time_q1,%.9f,Unoptimized execution time 25%% quantile\\n", unopt_time_q1);
    fprintf(metrics_file_ptr, "unopt_time_q3,%.9f,Unoptimized execution time 75%% quantile\\n", unopt_time_q3);
    
    // Write performance metrics - optimized
    fprintf(metrics_file_ptr, "opt_mean_time,%.9f,Optimized mean execution time (seconds)\\n", opt_mean_time);
    fprintf(metrics_file_ptr, "opt_median_time,%.9f,Optimized median execution time (seconds)\\n", opt_median_time);
    fprintf(metrics_file_ptr, "opt_min_time,%.9f,Optimized minimum execution time (seconds)\\n", sorted_opt_times[0]);
    fprintf(metrics_file_ptr, "opt_max_time,%.9f,Optimized maximum execution time (seconds)\\n", sorted_opt_times[iterations - 1]);
    fprintf(metrics_file_ptr, "opt_time_variance,%.9e,Optimized execution time variance\\n", opt_time_variance);
    fprintf(metrics_file_ptr, "opt_time_stddev,%.9e,Optimized execution time standard deviation\\n", opt_time_stddev);
    fprintf(metrics_file_ptr, "opt_time_q1,%.9f,Optimized execution time 25%% quantile\\n", opt_time_q1);
    fprintf(metrics_file_ptr, "opt_time_q3,%.9f,Optimized execution time 75%% quantile\\n", opt_time_q3);
    
    // Write speedup metrics
    fprintf(metrics_file_ptr, "mean_speedup,%.9f,Mean speedup (unopt/opt)\\n", unopt_mean_time / opt_mean_time);
    fprintf(metrics_file_ptr, "median_speedup,%.9f,Median speedup (unopt/opt)\\n", unopt_median_time / opt_median_time);"""

def write_accuracy_metrics() -> str:
    return """
    // Write accuracy metrics - reference values
    fprintf(metrics_file_ptr, "mpfr_value,%.17e,MPFR reference value\\n", mpfr_val);
    fprintf(metrics_file_ptr, "unopt_value,%.17e,Unoptimized result value\\n", unopt_first_val);
    
    // Write accuracy metrics - optimized results statistics
    fprintf(metrics_file_ptr, "opt_min_result,%.17e,Optimized minimum result\\n", opt_min_result);
    fprintf(metrics_file_ptr, "opt_max_result,%.17e,Optimized maximum result\\n", opt_max_result);
    fprintf(metrics_file_ptr, "opt_mean_result,%.17e,Optimized mean result\\n", opt_mean_result);
    fprintf(metrics_file_ptr, "opt_median_result,%.17e,Optimized median result\\n", opt_median_result);
    fprintf(metrics_file_ptr, "opt_result_variance,%.17e,Optimized result variance\\n", opt_result_variance);
    fprintf(metrics_file_ptr, "opt_result_stddev,%.17e,Optimized result standard deviation\\n", opt_result_stddev);
    fprintf(metrics_file_ptr, "opt_result_q1,%.17e,Optimized result 25%% quantile\\n", opt_result_q1);
    fprintf(metrics_file_ptr, "opt_result_q3,%.17e,Optimized result 75%% quantile\\n", opt_result_q3);"""

def write_error_metrics() -> str:
    return """
    // Write error metrics
    fprintf(metrics_file_ptr, "unopt_abs_error,%.17e,Absolute error: |Unopt - MPFR|\\n", unopt_error);
    fprintf(metrics_file_ptr, "opt_mean_abs_error,%.17e,Absolute error: |Opt (mean) - MPFR|\\n", opt_mean_error);
    
    if (mpfr_val != 0.0) {
      fprintf(metrics_file_ptr, "unopt_rel_error,%.17e,Relative error: |Unopt - MPFR|/|MPFR|\\n", unopt_rel_error);
      fprintf(metrics_file_ptr, "opt_mean_rel_error,%.17e,Relative error: |Opt (mean) - MPFR|/|MPFR|\\n", opt_mean_rel_error);
      fprintf(metrics_file_ptr, "unopt_ulps,%.9f,ULPs difference: Unopt vs MPFR\\n", get_ulps_value(unopt_rel_error));
      fprintf(metrics_file_ptr, "opt_mean_ulps,%.9f,ULPs difference: Opt (mean) vs MPFR\\n", get_ulps_value(opt_mean_rel_error));
    }"""

def write_optimized_results(opt_results_file: str) -> str:
    return f"""
  // Write optimized results file
  FILE *opt_results_file_ptr = fopen("{opt_results_file}", "w");
  if (!opt_results_file_ptr) {{
    fprintf(stderr, "Error: Could not open optimized results file for writing\\n");
  }} else {{
    // Write CSV header and data
    fprintf(opt_results_file_ptr, "iteration,result\\n");
    for (int i = 0; i < iterations; i++) {{
      fprintf(opt_results_file_ptr, "%d,%.17e\\n", i, opt_results[i]);
    }}
    fclose(opt_results_file_ptr);
    printf("Optimized results data written to %s\\n", "{opt_results_file}");
  }}"""

def write_optimized_timings(opt_timings_file: str) -> str:
    return f"""
  // Write optimized timings file
  FILE *opt_timings_file_ptr = fopen("{opt_timings_file}", "w");
  if (!opt_timings_file_ptr) {{
    fprintf(stderr, "Error: Could not open optimized timings file for writing\\n");
  }} else {{
    // Write CSV header and data
    fprintf(opt_timings_file_ptr, "iteration,time\\n");
    for (int i = 0; i < iterations; i++) {{
      fprintf(opt_timings_file_ptr, "%d,%.9f\\n", i, opt_times[i]);
    }}
    fclose(opt_timings_file_ptr);
    printf("Optimized timing data written to %s\\n", "{opt_timings_file}");
  }}"""

def write_unoptimized_timings(unopt_timings_file: str) -> str:
    return f"""
  // Write unoptimized timings file
  FILE *unopt_timings_file_ptr = fopen("{unopt_timings_file}", "w");
  if (!unopt_timings_file_ptr) {{
    fprintf(stderr, "Error: Could not open unoptimized timings file for writing\\n");
  }} else {{
    // Write CSV header and data
    fprintf(unopt_timings_file_ptr, "iteration,time\\n");
    for (int i = 0; i < iterations; i++) {{
      fprintf(unopt_timings_file_ptr, "%d,%.9f\\n", i, unopt_times[i]);
    }}
    fclose(unopt_timings_file_ptr);
    printf("Unoptimized timing data written to %s\\n", "{unopt_timings_file}");
  }}"""

def generate_metrics_csv_code(metrics_file: str, dimension: int, float_type: str, include_negatives: bool,
                            precision: int, opt_results_file: str, opt_timings_file: str, unopt_timings_file: str) -> str:
    # Generate all CSV writing components
    main_header = write_main_metrics_header(metrics_file)
    config_metrics = write_configuration_metrics(dimension, float_type, include_negatives, precision)
    perf_metrics = write_performance_metrics()
    acc_metrics = write_accuracy_metrics()
    err_metrics = write_error_metrics()
    opt_results_csv = write_optimized_results(opt_results_file)
    opt_timings_csv = write_optimized_timings(opt_timings_file)
    unopt_timings_csv = write_unoptimized_timings(unopt_timings_file)
    
    # Combine all components
    return f"""
{main_header}
{config_metrics}
{perf_metrics}
{acc_metrics}
{err_metrics}
    fclose(metrics_file_ptr);
    printf("\\nSummary metrics data written to %s\\n", "{metrics_file}");
  }}
{opt_results_csv}
{opt_timings_csv}
{unopt_timings_csv}
""" 