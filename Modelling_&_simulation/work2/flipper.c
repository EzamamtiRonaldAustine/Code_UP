/* Coin flipping simulation demo for CPSC 531 */
/*                                            */
/* Usage: cc -o flipper flipper.c             */
/*        ./flipper                           */

#include <stdio.h>
#include <stdlib.h>  /* ADDED: Required for rand() and srand() */
#include <time.h>    /* ADDED: Required if using time(NULL) */

#define NUMFLIPS 1000
#define DEBUG 1

/***********************************************************************/
/* RANDOM NUMBER GENERATION STUFF                      */
/***********************************************************************/

/* Generate a random floating point value uniformly distributed in [0,1] */
float Uniform01()
{
    float randnum;

    /* FIXED: Use rand() instead of random() */
    randnum = (float)rand();

    /* FIXED: Use RAND_MAX instead of the hardcoded 2147483647 
       This ensures the value is scaled between 0 and 1 correctly on any OS */
    randnum = randnum / (float)RAND_MAX; 

    return randnum;
}

/***********************************************************************/
/* MAIN PROGRAM                                        */
/***********************************************************************/

int main()
{
    int flips, heads, tails;

    /* FIXED: Use srand() instead of srandom() 
       Note: using time(NULL) makes it truly random every run. 
       If you want the SAME sequence every time, use srand(1234567); */
    // srand((unsigned int)time(NULL));
    srand(1234567);

    flips = 0;
    heads = 0;
    tails = 0;

    while( flips < NUMFLIPS )
    {
        float val;
        val = Uniform01();
        
        /* The logic remains identical to the original */
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
    printf("\nCoin Flipping Simulation\n");
    printf("Number of flips: %d\n", NUMFLIPS);
    printf("Number of heads: %d\n", heads);
    printf("Number of tails: %d\n", tails);
    printf("Observed probability of heads: %8.6f\n", (float)heads/NUMFLIPS);
#endif

    return 0;
}