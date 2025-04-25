decl_compare_doubles = """
// Function to compare doubles for qsort
int compare_doubles(const void *a, const void *b) {
  double diff = *(double*)a - *(double*)b;
  if (diff < 0) return -1;
  if (diff > 0) return 1;
  return 0;
}"""

decl_compare_floats = """
// Function to compare floats for qsort
int compare_floats(const void *a, const void *b) {
  float diff = *(float*)a - *(float*)b;
  if (diff < 0) return -1;
  if (diff > 0) return 1;
  return 0;
}"""

decl_variance = """
// Function to calculate variance of an array of doubles
double variance(double *arr, int n, double mean) {
  double var = 0.0;
  for (int i = 0; i < n; i++) {
    var += (arr[i] - mean) * (arr[i] - mean);
  }
  return var / n;
}"""

decl_variance_float = """
// Function to calculate variance of an array of floats
double variance_float(float *arr, int n, double mean) {
  double var = 0.0;
  for (int i = 0; i < n; i++) {
    var += ((double)arr[i] - mean) * ((double)arr[i] - mean);
  }
  return var / n;
}"""

decl_quantile = """
// Function to calculate quantile of a sorted array
double quantile(double *sorted_arr, int n, double q) {
  double index = (n - 1) * q;
  int lower = (int)floor(index);
  int upper = (int)ceil(index);
  if (lower == upper) {
    return sorted_arr[lower];
  } else {
    double weight = index - lower;
    return (1.0 - weight) * sorted_arr[lower] + weight * sorted_arr[upper];
  }
}"""

decl_quantile_float = """
// Function to calculate quantile of a sorted array of floats
double quantile_float(float *sorted_arr, int n, double q) {
  double index = (n - 1) * q;
  int lower = (int)floor(index);
  int upper = (int)ceil(index);
  if (lower == upper) {
    return sorted_arr[lower];
  } else {
    double weight = index - lower;
    return (1.0 - weight) * sorted_arr[lower] + weight * sorted_arr[upper];
  }
}"""

decl_estimate_ulps = """
// Function to estimate ULPs (Units in the Last Place) difference
// This is an approximation based on the relative error and float precision
const char* estimate_ulps(double rel_error) {
  static char ulps_str[64];
  
  if (rel_error == 0.0) {
    sprintf(ulps_str, "0 ULPs (exact match)");
    return ulps_str;
  }
  
  // IEEE 754 single precision has ~24 bits (23 explicitly stored + 1 implicit)
  // Converting relative error to ULPs is approximately:
  double est_ulps = rel_error * (1 << 24);
  
  if (est_ulps < 1.0) {
    sprintf(ulps_str, "<1 ULP (sub-bit precision error)");
  } else if (est_ulps < 1000) {
    sprintf(ulps_str, "~%.1f ULPs", est_ulps);
  } else {
    sprintf(ulps_str, "~%.1e ULPs", est_ulps);
  }
  
  return ulps_str;
}"""

decl_get_ulps_value = """
// Function to get numeric ULPs value for metrics output
double get_ulps_value(double rel_error) {
  if (rel_error == 0.0) {
    return 0.0;
  }
  
  // IEEE 754 single precision has ~24 bits (23 explicitly stored + 1 implicit)
  // Converting relative error to ULPs is approximately:
  return rel_error * (1 << 24);
}"""

def generate_statistic_functions() -> str:
    return f"""
{decl_compare_doubles}

{decl_compare_floats}

{decl_variance}

{decl_variance_float}

{decl_quantile}

{decl_quantile_float}

{decl_estimate_ulps}

{decl_get_ulps_value}
"""