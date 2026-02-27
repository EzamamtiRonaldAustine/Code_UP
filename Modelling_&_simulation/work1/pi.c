

/* Program to estimate Pi using Monte Carlo simulation */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SEED 1234567  /* initial seed for PRNG */

#define DEBUG 0     /* verbose debugging */

/* CHANGE: Fixed main signature to use char* argv[] for standard compliance */
int main(int argc, char* argv[])
  {
    int i, num;
    double x, y, z, pi;
    int count; /* points within upper-right quadrant of unit circle */

    printf("Enter the number of iterations to use in estimating pi: ");
    scanf("%d", &num);

    /* CHANGE: Replaced srandom with srand for Windows/MinGW portability */
    srand(SEED);  /* use fixed seed for reproducibility */
    /*    srandom(time(NULL)); /* to use the time of day as the seed */
   
    /* do the Monte Carlo simulation */
    count = 0;
    for( i = 0; i < num; i++ )
      {
	/* CHANGE: Replaced random() with rand() for Windows/MinGW portability */
	/* Logic: Map random integer to [0, 1] range */
	x = (double) rand()/RAND_MAX;
	y = (double) rand()/RAND_MAX;
#ifdef DEBUG
	printf("Random point is: (%g,%g)\n", x, y);
#endif

	/* compute z = f(x,y) */
	z = x*x+y*y;

	/* see if it is inside the unit circle or not */
	if( z <= 1.0 )
	  {
	    count++;
#ifdef DEBUG
	    printf("Yay! That point is INSIDE the unit circle\n");
#endif
	  }
#ifdef DEBUG
	else printf("That point is NOT inside the unit circle\n");
#endif
      }

    /* Logic: Pi estimate = 4 * (Points inside Quadrant / Total iterations) */
    /* Area of Circle / Area of Square = Pi*r^2 / (2r)^2 = Pi/4 */
    pi = (double) 4.0*count/num;
    
    printf("Number of trials: %d\n", num);
    printf("Estimate of pi: %g\n", pi);
  }