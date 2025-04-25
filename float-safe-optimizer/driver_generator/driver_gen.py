import re
import sys
import os
import subprocess
import argparse
from typing import Dict, List, Any, Tuple
from parser import parse_c_function, parse_rise_array_sizes, ParsingError
from rise_compile import compile_rise_to_c, edit_function_names
from floating_point_generation import get_float_value
from utils import ensure_out_dir

def generate_extended_driver(parsed_info: Dict[str, Any], rise_code: str, unopt_file: str, dimension: int = 256, precision: int = 256, float_type: str = "normal", iterations: int = 50, include_negatives: bool = False, metrics_file: str = "metrics.csv") -> str:
    # Get the base name from the file path
    base_name = os.path.basename(unopt_file).replace("_unopt.c", "")
    
    # Extract dimensions from RISE code
    parsed_rise = parse_rise_array_sizes(rise_code)
    dimensions = parsed_rise["dimensions"]
    
    # Derive file names for the different CSV outputs
    metrics_base = os.path.splitext(metrics_file)[0]
    opt_results_file = f"{metrics_base}_opt_results.csv"
    opt_timings_file = f"{metrics_base}_opt_timings.csv"
    unopt_timings_file = f"{metrics_base}_unopt_timings.csv"
    
    # Add sign randomization code for negative values if requested
    

    init_code = f"""
  // Initialize with normal floating point values
  for (int i = 0; i < {' * '.join([f"{dim}0" for dim in dimensions])}; i++) {{
    {get_float_value(float_type, include_negatives)}
    x0[i] = val;
    mpfr_init2(x0_mpfr[i], {precision});
    mpfr_set_d(x0_mpfr[i], val, MPFR_RNDN);
  }}"""
   
    
    # Add note about negative values if enabled
    neg_note = " with negative values" if include_negatives else ""
    
    driver_code = f"""#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <mpfr.h>
#include <float.h>
#include <string.h>

double get_time_in_seconds() {{
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return ts.tv_sec + ts.tv_nsec * 1e-9;
}}

extern void {base_name}_unopt(float* output, {', '.join([f"int {dim}0" for dim in dimensions])}, float* x0);
extern void {base_name}_opt(float* output, {', '.join([f"int {dim}0" for dim in dimensions])}, float* x0);
extern void {base_name}_mpfr(mpfr_t *output, {', '.join([f"int {dim}0" for dim in dimensions])}, mpfr_t *x0);

// Function to compare doubles for qsort
int compare_doubles(const void *a, const void *b) {{
  double diff = *(double*)a - *(double*)b;
  if (diff < 0) return -1;
  if (diff > 0) return 1;
  return 0;
}}

// Function to compare floats for qsort
int compare_floats(const void *a, const void *b) {{
  float diff = *(float*)a - *(float*)b;
  if (diff < 0) return -1;
  if (diff > 0) return 1;
  return 0;
}}

// Function to calculate variance of an array of doubles
double variance(double *arr, int n, double mean) {{
  double var = 0.0;
  for (int i = 0; i < n; i++) {{
    var += (arr[i] - mean) * (arr[i] - mean);
  }}
  return var / n;
}}

// Function to calculate variance of an array of floats
double variance_float(float *arr, int n, double mean) {{
  double var = 0.0;
  for (int i = 0; i < n; i++) {{
    var += ((double)arr[i] - mean) * ((double)arr[i] - mean);
  }}
  return var / n;
}}

// Function to calculate quantile of a sorted array
double quantile(double *sorted_arr, int n, double q) {{
  double index = (n - 1) * q;
  int lower = (int)floor(index);
  int upper = (int)ceil(index);
  if (lower == upper) {{
    return sorted_arr[lower];
  }} else {{
    double weight = index - lower;
    return (1.0 - weight) * sorted_arr[lower] + weight * sorted_arr[upper];
  }}
}}

// Function to calculate quantile of a sorted array of floats
double quantile_float(float *sorted_arr, int n, double q) {{
  double index = (n - 1) * q;
  int lower = (int)floor(index);
  int upper = (int)ceil(index);
  if (lower == upper) {{
    return sorted_arr[lower];
  }} else {{
    double weight = index - lower;
    return (1.0 - weight) * sorted_arr[lower] + weight * sorted_arr[upper];
  }}
}}

// Function to estimate ULPs (Units in the Last Place) difference
// This is an approximation based on the relative error and float precision
const char* estimate_ulps(double rel_error) {{
  static char ulps_str[64];
  
  if (rel_error == 0.0) {{
    sprintf(ulps_str, "0 ULPs (exact match)");
    return ulps_str;
  }}
  
  // IEEE 754 single precision has ~24 bits (23 explicitly stored + 1 implicit)
  // Converting relative error to ULPs is approximately:
  double est_ulps = rel_error * (1 << 24);
  
  if (est_ulps < 1.0) {{
    sprintf(ulps_str, "<1 ULP (sub-bit precision error)");
  }} else if (est_ulps < 1000) {{
    sprintf(ulps_str, "~%.1f ULPs", est_ulps);
  }} else {{
    sprintf(ulps_str, "~%.1e ULPs", est_ulps);
  }}
  
  return ulps_str;
}}

// Function to get numeric ULPs value for metrics output
double get_ulps_value(double rel_error) {{
  if (rel_error == 0.0) {{
    return 0.0;
  }}
  
  // IEEE 754 single precision has ~24 bits (23 explicitly stored + 1 implicit)
  // Converting relative error to ULPs is approximately:
  return rel_error * (1 << 24);
}}

int main(int argc, char** argv) {{
  // Set dimensions
  {' '.join([f"int {dim}0 = {dimension};" for dim in dimensions])}

  // Set random seed for reproducibility
  srand(42);

  // Set iterations count
  int iterations = {iterations};

  float* output_unopt = malloc(sizeof(float));  // Only need one output element
  float* output_opt = malloc(sizeof(float));    // Only need one output element
  float* x0 = malloc({' * '.join([f"{dim}0" for dim in dimensions])} * sizeof(float));
  mpfr_t *output_mpfr = malloc(sizeof(mpfr_t));  // Only need one output element
  mpfr_t *x0_mpfr = malloc({' * '.join([f"{dim}0" for dim in dimensions])} * sizeof(mpfr_t));

  // Arrays to track performance times for each iteration
  double* unopt_times = malloc(iterations * sizeof(double));
  double* opt_times = malloc(iterations * sizeof(double));
  
  // Array to track results of the optimized version for each iteration
  float* opt_results = malloc(iterations * sizeof(float));
  
  if (!output_unopt || !output_opt || !x0 || !output_mpfr || !x0_mpfr || 
      !unopt_times || !opt_times || !opt_results) {{
    fprintf(stderr, "Allocation failed.\\n");
    return EXIT_FAILURE;
  }}
{init_code}
  // Initialize only output_mpfr[0] for single value output
  mpfr_init2(output_mpfr[0], {precision});

  printf("Running benchmarks with {float_type}{neg_note} floating point values...\\n");
  
  // Run MPFR version once as ground truth
  printf("Running MPFR reference version (ground truth)...\\n");
  {base_name}_mpfr(output_mpfr, {', '.join([f"{dim}0" for dim in dimensions])}, x0_mpfr);
  double mpfr_val = mpfr_get_d(output_mpfr[0], MPFR_RNDN);
  printf("MPFR reference result: %e\\n", mpfr_val);
  
  // Initialize temporary MPFR variables for error calculations
  mpfr_t unopt_mpfr_temp, opt_mpfr_temp, mpfr_diff_unopt_temp, mpfr_diff_opt_temp;
  mpfr_init2(unopt_mpfr_temp, {precision});
  mpfr_init2(opt_mpfr_temp, {precision});
  mpfr_init2(mpfr_diff_unopt_temp, {precision});
  mpfr_init2(mpfr_diff_opt_temp, {precision});
  
  // Store unoptimized result for accuracy comparison
  double unopt_first_val;
  
  // Run all implementations for each iteration and track performance and results
  printf("Running %d iterations of benchmarks...\\n", iterations);
  for (int iter = 0; iter < iterations; iter++) {{
    // Run unoptimized version
    double start_time = get_time_in_seconds();
    {base_name}_unopt(output_unopt, {', '.join([f"{dim}0" for dim in dimensions])}, x0);
    double end_time = get_time_in_seconds();
    unopt_times[iter] = end_time - start_time;
    
    // Save the first unoptimized result for comparison
    if (iter == 0) {{
      unopt_first_val = output_unopt[0];
    }}
    
    // Run optimized version
    start_time = get_time_in_seconds();
    {base_name}_opt(output_opt, {', '.join([f"{dim}0" for dim in dimensions])}, x0);
    end_time = get_time_in_seconds();
    opt_times[iter] = end_time - start_time;
    
    // Store optimized result for this iteration
    opt_results[iter] = output_opt[0];
  }}
  
  // Sort the time arrays for calculating median and quantiles
  double* sorted_unopt_times = malloc(iterations * sizeof(double));
  double* sorted_opt_times = malloc(iterations * sizeof(double));
  memcpy(sorted_unopt_times, unopt_times, iterations * sizeof(double));
  memcpy(sorted_opt_times, opt_times, iterations * sizeof(double));
  qsort(sorted_unopt_times, iterations, sizeof(double), compare_doubles);
  qsort(sorted_opt_times, iterations, sizeof(double), compare_doubles);
  
  // Sort the optimized results for statistical analysis
  float* sorted_opt_results = malloc(iterations * sizeof(float));
  memcpy(sorted_opt_results, opt_results, iterations * sizeof(float));
  qsort(sorted_opt_results, iterations, sizeof(float), compare_floats);
  
  // Calculate mean times
  double unopt_mean_time = 0.0;
  double opt_mean_time = 0.0;
  for (int i = 0; i < iterations; i++) {{
    unopt_mean_time += unopt_times[i];
    opt_mean_time += opt_times[i];
  }}
  unopt_mean_time /= iterations;
  opt_mean_time /= iterations;
  
  // Calculate median times
  double unopt_median_time = sorted_unopt_times[iterations / 2];
  double opt_median_time = sorted_opt_times[iterations / 2];
  
  // Calculate variance and std deviation of times
  double unopt_time_variance = variance(unopt_times, iterations, unopt_mean_time);
  double opt_time_variance = variance(opt_times, iterations, opt_mean_time);
  double unopt_time_stddev = sqrt(unopt_time_variance);
  double opt_time_stddev = sqrt(opt_time_variance);
  
  // Calculate quantiles of times
  double unopt_time_q1 = quantile(sorted_unopt_times, iterations, 0.25);
  double unopt_time_q3 = quantile(sorted_unopt_times, iterations, 0.75);
  double opt_time_q1 = quantile(sorted_opt_times, iterations, 0.25);
  double opt_time_q3 = quantile(sorted_opt_times, iterations, 0.75);
  
  // Calculate mean of optimized results
  double opt_mean_result = 0.0;
  for (int i = 0; i < iterations; i++) {{
    opt_mean_result += opt_results[i];
  }}
  opt_mean_result /= iterations;
  
  // Calculate median of optimized results
  double opt_median_result = sorted_opt_results[iterations / 2];
  
  // Calculate variance and std deviation of optimized results
  double opt_result_variance = variance_float(opt_results, iterations, opt_mean_result);
  double opt_result_stddev = sqrt(opt_result_variance);
  
  // Calculate quantiles of optimized results
  double opt_result_q1 = quantile_float(sorted_opt_results, iterations, 0.25);
  double opt_result_q3 = quantile_float(sorted_opt_results, iterations, 0.75);
  
  // Calculate min/max optimized results
  float opt_min_result = sorted_opt_results[0];
  float opt_max_result = sorted_opt_results[iterations - 1];
  
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
  double opt_mean_rel_error = (mpfr_val != 0.0) ? (opt_mean_error / fabs(mpfr_val)) : 0.0;
  
  printf("\\n╔════════════════════════════════════════════════════════════════╗\\n");
  printf("║                     ACCURACY COMPARISON                        ║\\n");
  printf("╚════════════════════════════════════════════════════════════════╝\\n\\n");
  
  printf("Reference values:\\n");
  printf("  MPFR (ground truth): %e\\n", mpfr_val);
  printf("  Unoptimized:         %e\\n", unopt_first_val);
  printf("  Optimized (mean):    %e\\n\\n", opt_mean_result);
  
  printf("Optimized results statistics across %d iterations:\\n", iterations);
  printf("  Minimum:      %e\\n", opt_min_result);
  printf("  Maximum:      %e\\n", opt_max_result);
  printf("  Mean:         %e\\n", opt_mean_result);
  printf("  Median:       %e\\n", opt_median_result);
  printf("  Variance:     %e\\n", opt_result_variance);
  printf("  Std. Dev:     %e\\n", opt_result_stddev);
  printf("  25%% Quantile: %e\\n", opt_result_q1);
  printf("  75%% Quantile: %e\\n\\n", opt_result_q3);
  
  printf("Absolute Differences (vs MPFR reference):\\n");
  printf("  |Unopt - MPFR|:        %e\\n", unopt_error);
  printf("  |Opt (mean) - MPFR|:   %e\\n\\n", opt_mean_error);
  
  printf("Relative Differences (vs MPFR reference):\\n");
  if (mpfr_val != 0.0) {{
    // Format as "1 part in X" ratio (more intuitive)
    if (unopt_rel_error > 0) {{
      printf("  |Unopt - MPFR|:        1 part in %.0f\\n", 1.0/unopt_rel_error);
    }} else {{
      printf("  |Unopt - MPFR|:        Exact match\\n");
    }}
    
    if (opt_mean_rel_error > 0) {{
      printf("  |Opt (mean) - MPFR|:   1 part in %.0f\\n", 1.0/opt_mean_rel_error);
    }} else {{
      printf("  |Opt (mean) - MPFR|:   Exact match\\n");
    }}
    
    // Also show estimated ULPs (Units in the Last Place)
    printf("\\nBinary precision errors (estimated):\\n");
    printf("  |Unopt - MPFR|:        %s\\n", estimate_ulps(unopt_rel_error));
    printf("  |Opt (mean) - MPFR|:   %s\\n", estimate_ulps(opt_mean_rel_error));
  }} else {{
    printf("  (Cannot calculate relative differences - MPFR value is zero)\\n");
  }}
  
  printf("\\n╔════════════════════════════════════════════════════════════════╗\\n");
  printf("║                   PERFORMANCE COMPARISON                       ║\\n");
  printf("╚════════════════════════════════════════════════════════════════╝\\n\\n");
  
  printf("Execution time statistics across %d iterations:\\n\\n", iterations);
  
  printf("Unoptimized version:\\n");
  printf("  Mean:         %.9f seconds\\n", unopt_mean_time);
  printf("  Median:       %.9f seconds\\n", unopt_median_time);
  printf("  Minimum:      %.9f seconds\\n", sorted_unopt_times[0]);
  printf("  Maximum:      %.9f seconds\\n", sorted_unopt_times[iterations - 1]);
  printf("  Variance:     %.9e\\n", unopt_time_variance);
  printf("  Std. Dev:     %.9e\\n", unopt_time_stddev);
  printf("  25%% Quantile: %.9f seconds\\n", unopt_time_q1);
  printf("  75%% Quantile: %.9f seconds\\n\\n", unopt_time_q3);
  
  printf("Optimized version:\\n");
  printf("  Mean:         %.9f seconds\\n", opt_mean_time);
  printf("  Median:       %.9f seconds\\n", opt_median_time);
  printf("  Minimum:      %.9f seconds\\n", sorted_opt_times[0]);
  printf("  Maximum:      %.9f seconds\\n", sorted_opt_times[iterations - 1]);
  printf("  Variance:     %.9e\\n", opt_time_variance);
  printf("  Std. Dev:     %.9e\\n", opt_time_stddev);
  printf("  25%% Quantile: %.9f seconds\\n", opt_time_q1);
  printf("  75%% Quantile: %.9f seconds\\n\\n", opt_time_q3);
  
  printf("Performance metrics:\\n");
  printf("  Mean speedup:   %.2fx\\n", unopt_mean_time / opt_mean_time);
  printf("  Median speedup: %.2fx\\n", unopt_median_time / opt_median_time);

  // Create four separate CSV files
  // 1. Main metrics file
  FILE *metrics_file_ptr = fopen("{metrics_file}", "w");
  if (!metrics_file_ptr) {{
    fprintf(stderr, "Error: Could not open metrics file for writing\\n");
  }} else {{
    // Write CSV header
    fprintf(metrics_file_ptr, "metric,value,description\\n");
    
    // Write configuration parameters
    fprintf(metrics_file_ptr, "dimension,%d,Array dimension size\\n", {dimension});
    fprintf(metrics_file_ptr, "float_type,%s,Type of floating point values\\n", "{float_type}");
    fprintf(metrics_file_ptr, "include_negatives,%s,Whether negative values were included\\n", "{str(include_negatives).lower()}");
    fprintf(metrics_file_ptr, "precision,%d,MPFR precision bits\\n", {precision});
    fprintf(metrics_file_ptr, "iterations,%d,Number of benchmark iterations\\n", iterations);

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
    fprintf(metrics_file_ptr, "median_speedup,%.9f,Median speedup (unopt/opt)\\n", unopt_median_time / opt_median_time);
    
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
    fprintf(metrics_file_ptr, "opt_result_q3,%.17e,Optimized result 75%% quantile\\n", opt_result_q3);
    
    // Write error metrics
    fprintf(metrics_file_ptr, "unopt_abs_error,%.17e,Absolute error: |Unopt - MPFR|\\n", unopt_error);
    fprintf(metrics_file_ptr, "opt_mean_abs_error,%.17e,Absolute error: |Opt (mean) - MPFR|\\n", opt_mean_error);
    
    if (mpfr_val != 0.0) {{
      fprintf(metrics_file_ptr, "unopt_rel_error,%.17e,Relative error: |Unopt - MPFR|/|MPFR|\\n", unopt_rel_error);
      fprintf(metrics_file_ptr, "opt_mean_rel_error,%.17e,Relative error: |Opt (mean) - MPFR|/|MPFR|\\n", opt_mean_rel_error);
      fprintf(metrics_file_ptr, "unopt_ulps,%.9f,ULPs difference: Unopt vs MPFR\\n", get_ulps_value(unopt_rel_error));
      fprintf(metrics_file_ptr, "opt_mean_ulps,%.9f,ULPs difference: Opt (mean) vs MPFR\\n", get_ulps_value(opt_mean_rel_error));
    }}
    
    fclose(metrics_file_ptr);
    printf("\\nSummary metrics data written to %s\\n", "{metrics_file}");
  }}
  
  // 2. Optimized results file
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
  }}
  
  // 3. Optimized timings file
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
  }}
  
  // 4. Unoptimized timings file
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
  }}

  // Free memory and clean up
  free(output_unopt);
  free(output_opt);
  free(x0);
  mpfr_clear(output_mpfr[0]);
  for (int i = 0; i < {' * '.join([f"{dim}0" for dim in dimensions])}; i++) {{
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

  return EXIT_SUCCESS;
}}
"""
    return driver_code


def main():
    """Main entry point for the driver generator."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate a driver for RISE code with MPFR comparison')
    parser.add_argument('unopt_rise_file', help='Path to the unoptimized RISE source file')
    parser.add_argument('-o', '--opt_rise_file', help='Path to the optimized RISE source file (optional)')
    parser.add_argument('-d', '--dimension', type=int, default=256, 
                        help='Dimension size for all dimensions (default: 256)')
    parser.add_argument('-i', '--iterations', type=int, default=50,
                        help='Number of iterations for the benchmark (default: 50)')
    parser.add_argument('-p', '--precision', type=int, default=256,
                        help='MPFR precision in bits (default: 256)')
    parser.add_argument('--output', default='driver_compare.c',
                        help='Output driver file name (default: driver_compare.c)')
    parser.add_argument('-f', '--float_type', default='normal', 
                        choices=['normal', 'subnormal', 'mixed', 'magnitude'],
                        help='Type of floating point numbers to generate: normal (default), subnormal, mixed (normal+subnormal), or magnitude (high+low)')
    parser.add_argument('--prefix', default='',
                        help='Prefix to add to all generated files (default: none)')
    parser.add_argument('--include_negatives', action='store_true',
                        help='Include negative numbers in the generated floating-point values')
    parser.add_argument('--metrics_file', default='metrics.csv',
                        help='Output file for performance and accuracy metrics (default: metrics.csv)')
    args = parser.parse_args()

    unopt_rise_file = args.unopt_rise_file
    opt_rise_file = args.opt_rise_file
    dimension = args.dimension
    precision = args.precision
    output_file_name = args.output
    iterations = args.iterations
    float_type = args.float_type
    prefix = args.prefix
    include_negatives = args.include_negatives
    metrics_file = args.metrics_file
    
    out_dir = ensure_out_dir()
    
    # Apply prefix to metrics file name if provided
    if prefix and not metrics_file.startswith(prefix):
        metrics_file = f"{prefix}{metrics_file}"
    
    # Put metrics file in output directory
    metrics_file_path = os.path.join(out_dir, metrics_file)
    
    try:
        # First, read the unoptimized RISE code
        with open(unopt_rise_file, "r") as f:
            unopt_rise_code = f.read()

        # Compile RISE to all versions
        print(f"Compiling {unopt_rise_file} to C (all versions)...")
        if opt_rise_file:
            print(f"Using optimized version from {opt_rise_file}")
            c_file_unopt, c_file_mpfr_unopt, c_file_opt = compile_rise_to_c(unopt_rise_file, opt_rise_file, prefix)
        else:
            print("No optimized version provided, using unoptimized for all versions")
            c_file_unopt, c_file_mpfr_unopt, c_file_opt = compile_rise_to_c(unopt_rise_file, None, prefix)
            
        print(f"Successfully compiled to unoptimized: {c_file_unopt}")
        print(f"Successfully compiled to unoptimized MPFR: {c_file_mpfr_unopt}")
        print(f"Successfully compiled to optimized: {c_file_opt}")

        # Rename functions in all files to ensure they have correct names
        edit_function_names(c_file_unopt, c_file_mpfr_unopt, c_file_opt)

        # Read the unoptimized C code for parsing (could use any of the versions)
        with open(c_file_unopt, "r") as f:
            c_code_unopt = f.read()

    except FileNotFoundError as e:
        print(f"Error: Could not find file '{e.filename}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error during compilation: {str(e)}")
        sys.exit(1)

    try:
        parsed_info_c = parse_c_function(c_code_unopt)
        parsed_info_rise = parse_rise_array_sizes(unopt_rise_code)
    except (ParsingError, ValueError) as e:
        print(f"Error parsing C code: {e}")
        sys.exit(1)

    # Generate extended driver code
    driver_code = generate_extended_driver(parsed_info_c, unopt_rise_code, c_file_unopt, 
                                         dimension, precision, float_type, iterations,
                                         include_negatives, metrics_file_path)

    # Apply prefix to output file name if provided
    if prefix and not output_file_name.startswith(prefix):
        output_file_name = f"{prefix}{output_file_name}"

    # Write the driver code to a file in the out directory
    output_file = os.path.join(out_dir, output_file_name)

    with open(output_file, "w") as f:
        f.write(driver_code)

    print(f"Successfully generated {output_file}")

    # Compile the comparison driver with gcc
    try:
        # Apply prefix to executable name if provided
        executable_name = os.path.join(out_dir, os.path.splitext(output_file_name)[0])
        cmd = ["gcc", "-o", executable_name, output_file, c_file_unopt, c_file_mpfr_unopt, c_file_opt, "-lm", "-lmpfr", "-fopenmp"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully compiled {executable_name}")
        else:
            print("Compilation failed:")
            print(result.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error during compilation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
