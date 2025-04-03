
#include <stdint.h>

void foo(float* output, int n0, float* x0){
  /* reduceSeq */
  {
    float x1914;
    /* non-MPFR type */
    x1914 = 0.0f;
    for (int i_1922 = 0; i_1922 < n0; i_1922 = 1 + i_1922) {
      x1914 = x1914 + x0[i_1922];
    }
    
    output[0] = x1914;
    /* non-MPFR type */
  }
  
}

