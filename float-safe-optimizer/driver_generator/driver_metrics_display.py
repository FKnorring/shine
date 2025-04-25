from typing import List, Tuple

def display_accuracy_comparison() -> str:
    return """
  printf("\\n╔════════════════════════════════════════════════════════════════╗\\n");
  printf("║                     ACCURACY COMPARISON                        ║\\n");
  printf("╚════════════════════════════════════════════════════════════════╝\\n\\n");
  
  printf("Reference values:\\n");
  printf("  MPFR (ground truth): %e\\n", mpfr_val);
  printf("  Unoptimized:         %e\\n", unopt_first_val);
  printf("  Optimized (mean):    %e\\n\\n", opt_mean_result);"""

def display_optimized_results_stats() -> str:
    return """
  printf("Optimized results statistics across %d iterations:\\n", iterations);
  printf("  Minimum:      %e\\n", opt_min_result);
  printf("  Maximum:      %e\\n", opt_max_result);
  printf("  Mean:         %e\\n", opt_mean_result);
  printf("  Median:       %e\\n", opt_median_result);
  printf("  Variance:     %e\\n", opt_result_variance);
  printf("  Std. Dev:     %e\\n", opt_result_stddev);
  printf("  25%% Quantile: %e\\n", opt_result_q1);
  printf("  75%% Quantile: %e\\n\\n", opt_result_q3);"""

def display_absolute_differences() -> str:
    return """
  printf("Absolute Differences (vs MPFR reference):\\n");
  printf("  |Unopt - MPFR|:        %e\\n", unopt_error);
  printf("  |Opt (mean) - MPFR|:   %e\\n\\n", opt_mean_error);"""

def display_relative_differences() -> str:
    return """
  printf("Relative Differences (vs MPFR reference):\\n");
  if (mpfr_val != 0.0) {
    // Format as "1 part in X" ratio (more intuitive)
    if (unopt_rel_error > 0) {
      printf("  |Unopt - MPFR|:        1 part in %.0f\\n", 1.0/unopt_rel_error);
    } else {
      printf("  |Unopt - MPFR|:        Exact match\\n");
    }
    
    if (opt_mean_rel_error > 0) {
      printf("  |Opt (mean) - MPFR|:   1 part in %.0f\\n", 1.0/opt_mean_rel_error);
    } else {
      printf("  |Opt (mean) - MPFR|:   Exact match\\n");
    }
    
    // Also show estimated ULPs (Units in the Last Place)
    printf("\\nBinary precision errors (estimated):\\n");
    printf("  |Unopt - MPFR|:        %s\\n", estimate_ulps(unopt_rel_error));
    printf("  |Opt (mean) - MPFR|:   %s\\n", estimate_ulps(opt_mean_rel_error));
  } else {
    printf("  (Cannot calculate relative differences - MPFR value is zero)\\n");
  }"""

def display_performance_comparison() -> str:
    return """
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
  printf("  Median speedup: %.2fx\\n", unopt_median_time / opt_median_time);"""

def generate_metrics_display_code() -> str:
    # Generate all display components
    accuracy = display_accuracy_comparison()
    opt_stats = display_optimized_results_stats()
    abs_diffs = display_absolute_differences()
    rel_diffs = display_relative_differences()
    perf_comp = display_performance_comparison()
    
    # Combine all components
    return f"""
{accuracy}
{opt_stats}
{abs_diffs}
{rel_diffs}
{perf_comp}
""" 