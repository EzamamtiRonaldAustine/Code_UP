/* Coin flipping simulation demo for CPSC 531 */
/*                                            */
/* Usage: cc -o flipper flipper.c             */
/*        ./flipper                           */

#include <stdio.h>

#define NUMFLIPS 10

/* Number of coin flips to simulate */

/* Debugging output */
#define DEBUG 1

/***********************************************************************/
/*                 RANDOM NUMBER GENERATION STUFF                      */
/***********************************************************************/

/* Parameters for random number generation. */
#define MAX_INT 2147483647       /* Maximum positive integer 2^31 - 1 */

/* Generate a random floating point value uniformly distributed in [0,1] */
float Uniform01()
  {
    float randnum;

    /* get a random positive integer from random() */
    randnum = (float) 1.0 * random();

    /* divide by max int to get something in (0..1)  */
    randnum = (float) randnum / (1.0 * MAX_INT); 

    return( randnum );
  }

/***********************************************************************/
/*                 MAIN PROGRAM                                        */
/***********************************************************************/

int main()
  {
    int flips, heads, tails;

    /* Initialization */
    srandom(1234567);
    flips = 0;
    heads = 0;
    tails = 0;

    while( flips < NUMFLIPS )
      {
	float val;
	val = Uniform01();
	if( val < 0.50 )
	  {
	    printf("H\n");
	    heads++;
	  }
	else
	  {
	    printf("T\n");
	    tails++;
	  }
	flips++;
      }

#ifdef DEBUG
    printf("\n");
    printf("Coin Flipping Simulation\n");
    printf("Number of flips: %d\n", NUMFLIPS);
    printf("Number of heads: %d\n", heads);
    printf("Number of tails: %d\n", tails);
    printf("Observed probability of heads: %8.6f\n", 1.0*heads/NUMFLIPS);
#endif
  }
