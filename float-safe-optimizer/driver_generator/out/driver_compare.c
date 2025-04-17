#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <mpfr.h>

double get_time_in_seconds() {
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return ts.tv_sec + ts.tv_nsec * 1e-9;
}

extern void foo(float* output, int n0, float* x0);
extern void foo_mpfr(mpfr_t *output, int n0, mpfr_t *x0);

int main(int argc, char** argv) {
  // Set dimensions
  int n0 = 256; // dimension size for n0

  float* output = malloc(n0 * sizeof(float));
  float* x0 = malloc(n0 * sizeof(float));
  mpfr_t *output_mpfr = malloc(n0 * sizeof(mpfr_t));
  mpfr_t *x0_mpfr = malloc(n0 * sizeof(mpfr_t));

  if (!output || !x0 || !output_mpfr || !x0_mpfr) {
    fprintf(stderr, "Allocation failed.\n");
    return EXIT_FAILURE;
  }

  for (int i = 0; i < n0; i++) {
    float val = (float)rand() / RAND_MAX;
    x0[i] = val;
    mpfr_init2(x0_mpfr[i], 256);
    mpfr_set_d(x0_mpfr[i], val, MPFR_RNDN);
  }
  for (int i = 0; i < n0; i++) {
    mpfr_init2(output_mpfr[i], 256);
  }

  // Standard version benchmark
  int iterations = 50;
  double start_time = get_time_in_seconds();
  for (int iter = 0; iter < iterations; iter++) {
    foo(output, n0, x0);
  }
  double end_time = get_time_in_seconds();
  double standard_time = (end_time - start_time) / iterations;
  printf("Standard version: %f seconds per iteration\n", standard_time);

  // MPFR version benchmark
  start_time = get_time_in_seconds();
  for (int iter = 0; iter < iterations; iter++) {
    foo_mpfr(output_mpfr, n0, x0_mpfr);
  }
  end_time = get_time_in_seconds();
  double mpfr_time = (end_time - start_time) / iterations;
  printf("MPFR version: %f seconds per iteration\n", mpfr_time);

  // Accuracy comparison
  mpfr_t max_diff, avg_diff, diff, temp;
  mpfr_init2(max_diff, 256);
  mpfr_init2(avg_diff, 256);
  mpfr_init2(diff, 256);
  mpfr_init2(temp, 256);
  
  mpfr_set_d(max_diff, 0.0, MPFR_RNDN);
  mpfr_set_d(avg_diff, 0.0, MPFR_RNDN);
  
  for (int i = 0; i < n0; i++) {
    // Convert float output to mpfr
    mpfr_set_d(temp, output[i], MPFR_RNDN);
    // Calculate |output_mpfr[i] - temp|
    mpfr_sub(diff, output_mpfr[i], temp, MPFR_RNDN);
    mpfr_abs(diff, diff, MPFR_RNDN);
    
    // Update max_diff
    if (mpfr_cmp(diff, max_diff) > 0) {
      mpfr_set(max_diff, diff, MPFR_RNDN);
    }
    
    // Update avg_diff
    mpfr_add(avg_diff, avg_diff, diff, MPFR_RNDN);
  }
  
  // Calculate average
  mpfr_div_ui(avg_diff, avg_diff, n0, MPFR_RNDN);
  
  printf("\nAccuracy Comparison:\n");
  printf("  Maximum absolute error: %e\n", mpfr_get_d(max_diff, MPFR_RNDN));
  printf("  Average absolute error: %e\n", mpfr_get_d(avg_diff, MPFR_RNDN));
  printf("\nMPFR Slowdown: %.2fx\n", mpfr_time / standard_time);

  free(output);
  free(x0);
  for (int i = 0; i < n0; i++) {
    mpfr_clear(output_mpfr[i]);
  }
  for (int i = 0; i < n0; i++) {
    mpfr_clear(x0_mpfr[i]);
  }
  free(output_mpfr);
  free(x0_mpfr);
  
  // Clear MPFR variables used for error calculation
  mpfr_clear(max_diff);
  mpfr_clear(avg_diff);
  mpfr_clear(diff);
  mpfr_clear(temp);

  return EXIT_SUCCESS;
}