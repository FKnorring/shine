#include <stdio.h>
#include <stdlib.h>
#include <time.h>

double get_time_in_seconds() {
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return ts.tv_sec + ts.tv_nsec * 1e-9;
}

extern void foo(float* output, int n0, int n1, int n2, float* x0, float* x1);

int main(int argc, char** argv) {
  // Set default dimensions
  int n0 = 256; // default value for n0
  int n1 = 256; // default value for n1
  int n2 = 256; // default value for n2

  float* output = malloc(n0 * n1 * sizeof(float));
  float* x0 = malloc(n0 * n2 * sizeof(float));
  float* x1 = malloc(n1 * n2 * sizeof(float));

  if (!output || !x0 || !x1) {
    fprintf(stderr, "Allocation failed.\n");
    return EXIT_FAILURE;
  }

  for (int i = 0; i < n0 * n2; i++) {
    x0[i] = (float)rand() / RAND_MAX;
  }
  for (int i = 0; i < n1 * n2; i++) {
    x1[i] = (float)rand() / RAND_MAX;
  }

  // Warm up call
  foo(output, n0, n1, n2, x0, x1);

  int iterations = 50;
  double start_time = get_time_in_seconds();
  for (int iter = 0; iter < iterations; iter++) {
    foo(output, n0, n1, n2, x0, x1);
  }
  double end_time = get_time_in_seconds();
  double total_time = end_time - start_time;
  double average_time = total_time / iterations;

  printf("Total execution time over %d iterations: %f seconds\n", iterations, total_time);
  printf("Average execution time: %f seconds per call\n", average_time);

  free(output);
  free(x0);
  free(x1);

  return EXIT_SUCCESS;
}