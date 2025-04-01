
#include <stdint.h>
#include <mpfr.h>

void foo(float* output, int n0, int n1, int n2, float* x0, float* x1){
  /* mapSeq */
  for (int i_2010 = 0; i_2010 < n0; i_2010 = 1 + i_2010) {
    /* mapSeq */
    for (int i_2011 = 0; i_2011 < n1; i_2011 = 1 + i_2011) {
      /* reduceSeq */
      {
        float x1986;
        x1986 = 0.0f;
        for (int i_2012 = 0; i_2012 < n2; i_2012 = 1 + i_2012) {
          x1986 = x1986 + (x0[i_2010 + (i_2012 * n0)] * x1[i_2011 + (i_2012 * n1)]);
        }
        
        output[i_2011 + (i_2010 * n1)] = x1986;
      }
      
    }
    
  }
  
}

