

/* Program to estimate Pi using Monte Carlo simulation */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SEED 1234567  /* initial seed for PRNG */

#define DEBUG 1     /* verbose debugging */

int main(int argc, char* argv)
  {
    int i, num;
    double x, y, z, pi;
    int count; /* points within upper-right quadrant of unit circle */

    printf("Enter the number of iterations to use in estimating pi: ");
    scanf("%d", &num);

    /* initialize random numbers */
    srandom(SEED);  /* to use the seed specified above */
    /*    srandom(time(NULL)); /* to use the time of day as the seed */
   
    /* do the Monte Carlo simulation */
    count = 0;
    for( i = 0; i < num; i++ )
      {
	/* generate a uniformly random U(0,1) point in x-y dimensions */
	x = (double) random()/RAND_MAX;
	y = (double) random()/RAND_MAX;
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

    /* scale the estimate back up to the full circle */
    pi = (double) 4.0*count/num;
    
    printf("Number of trials: %d\n", num);
    printf("Estimate of pi: %g\n", pi);
  }