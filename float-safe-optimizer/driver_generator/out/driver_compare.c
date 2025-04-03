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
  int n0 = 2048; // dimension size for n0

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
    mpfr_init2(x0_mpfr[i], 512);
    mpfr_set_d(x0_mpfr[i], val, MPFR_RNDN);
  }
  for (int i = 0; i < n0; i++) {
    mpfr_init2(output_mpfr[i], 512);
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
  double max_diff = 0.0;
  double avg_diff = 0.0;
  for (int i = 0; i < n0; i++) {
    double mpfr_val = mpfr_get_d(output_mpfr[i], MPFR_RNDN);
    double diff = fabs(output[i] - mpfr_val);
    max_diff = fmax(max_diff, diff);
    avg_diff += diff;
  }
  avg_diff /= n0;
  printf("\nAccuracy Comparison:\n");
  printf("  Maximum absolute error: %e\n", max_diff);
  printf("  Average absolute error: %e\n", avg_diff);
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

  return EXIT_SUCCESS;
}