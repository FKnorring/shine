
#include <stdint.h>

void sum_opt(float* output, int n0, float* x0){
  {
    float x1956[n0 / 128];
    /* non-MPFR type */
    #pragma omp parallel for
    for (int i_1973 = 0; i_1973 < (n0 / 128); i_1973 = 1 + i_1973) {
      /* reduceSeq */
      {
        float x1962;
        /* non-MPFR type */
        x1962 = 0.0f;
        for (int i_1974 = 0; i_1974 < 128; i_1974 = 1 + i_1974) {
          x1962 = x1962 + x0[i_1974 + (128 * i_1973)];
        }
        
        x1956[i_1973] = x1962;
        /* non-MPFR type */
      }
      
    }
    
    /* reduceSeq */
    {
      float x1948;
      /* non-MPFR type */
      x1948 = 0.0f;
      for (int i_1975 = 0; i_1975 < (n0 / 128); i_1975 = 1 + i_1975) {
        x1948 = x1948 + x1956[i_1975];
      }
      
      output[0] = x1948;
      /* non-MPFR type */
    }
    
    /* non-MPFR type */
  }
  
}

