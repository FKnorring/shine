CC=gcc
CFLAGS=-fopenmp -O3
LDFLAGS=-lrt -lmpfr -lgmp

# Regular float version targets
float: mm.o mm_par.o driver.o
	$(CC) $(CFLAGS) -o driver $^ $(LDFLAGS)

# MPFR version targets
mpfr: mm_mpfr.o mm_par_mpfr.o driver_mpfr.o
	$(CC) $(CFLAGS) -o driver_mpfr $^ $(LDFLAGS)

# Comparison version target
compare: mm.o mm_par.o mm_mpfr.o mm_par_mpfr.o driver_compare.o
	$(CC) $(CFLAGS) -o driver_compare $^ $(LDFLAGS) -lm

# Object files for float version
driver.o: driver.c
	$(CC) $(CFLAGS) -c driver.c

mm.o: mm.c
	$(CC) $(CFLAGS) -c mm.c

mm_par.o: mm_par.c
	$(CC) $(CFLAGS) -c mm_par.c

# Object files for MPFR version
driver_mpfr.o: driver_mpfr.c
	$(CC) $(CFLAGS) -c driver_mpfr.c

mm_mpfr.o: mm_mpfr.c
	$(CC) $(CFLAGS) -c mm_mpfr.c

mm_par_mpfr.o: mm_par_mpfr.c
	$(CC) $(CFLAGS) -c mm_par_mpfr.c

# Object file for comparison driver
driver_compare.o: driver_compare.c
	$(CC) $(CFLAGS) -c driver_compare.c

# Clean target
clean:
	rm -f *.o driver driver_mpfr driver_compare

# Default target builds all versions
all: float mpfr compare

.PHONY: clean all float mpfr compare 