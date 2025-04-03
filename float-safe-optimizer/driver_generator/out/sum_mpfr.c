
#include <stdint.h>
#include <mpfr.h>

void foo_mpfr(mpfr_t* output, int n0, mpfr_t* x0){
  /* reduceSeq */
  {
    mpfr_t x1914;
    mpfr_init2(x1914, 256);
    mpfr_set_d(x1914, 0.0f, MPFR_RNDN);
    for (int i_1922 = 0; i_1922 < n0; i_1922 = 1 + i_1922) {
      mpfr_add(x1914, x1914, x0[i_1922], MPFR_RNDN);
    }
    
    mpfr_set(output[0], x1914, MPFR_RNDN);
    mpfr_clear(x1914);
  }
  
}

