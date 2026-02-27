/* ===============================================================
   RANDOM DISTRIBUTION DEMONSTRATION PROGRAM
   ---------------------------------------------------------------
   This program generates random numbers from several probability
   distributions:

   1. Uniform Distribution U(0,1)
   2. Geometric Distribution
   3. Exponential Distribution
   4. Normal Distribution
   5. Lognormal Distribution

   The program prints 20 observations from each distribution.

   IMPORTANT CHANGES FROM ORIGINAL VERSION
   ---------------------------------------
   1. Removed erand48() (not supported on Windows)
   2. Replaced rejection method with Box-Muller method
      for Normal distribution.
   3. Added srand(time(NULL)) for true randomness.
   4. FIXED Uniform01() using RAND_MAX.
   5. Added definition of M_PI for Windows.

   Compile:

   gcc demo.c -o demo -lm

   Run:

   demo
   =============================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>


/* ===============================================================
   ASSIGNMENT UPDATE 1
   Define M_PI constant for Windows compatibility
   ---------------------------------------------------------------
   Some Windows compilers do not define M_PI in math.h.
   The Box-Muller formula requires π.

   Without this definition:
   Compilation may fail.
   =============================================================== */

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif


/* Number of samples to generate */
#define NUM_VALUES 200



/* Function Prototypes */

double Uniform01();
double Normal(float mean, float std);
double Lognormal(float mean, float std);
double Exponential(double mu);
int Geometric(double m);



/* ===============================================================
   MAIN PROGRAM
   =============================================================== */

int main()
{
    int i, geom;

    double norm, lognorm, expo, uni;

    float nmean, nstd;
    float logmean, logstd;
    float emean, gmean;



    /* -----------------------------------------------------------
       Initialize Random Seed

       Ensures different random numbers each run.
       ----------------------------------------------------------- */

    srand(time(NULL));



    /* -----------------------------------------------------------
       Distribution Parameters
       ----------------------------------------------------------- */

    gmean = 14.0;      /* Mean of geometric distribution */
    emean = 0.352;     /* Mean of exponential distribution */

    nmean = 0.0;       /* Normal mean */
    nstd  = 1.0;       /* Normal standard deviation */

    logmean = 5.9651;  /* Lognormal mean */
    logstd  = 0.4832;  /* Lognormal standard deviation */



    printf(" Obs     U(0,1)   Geom     Exp     Norm(0,1)  LogNorm(m,s)\n");
    printf("---------------------------------------------------------\n");



    /* Generate Samples */

    for(i = 1; i <= NUM_VALUES; i++)
    {
        uni = Uniform01();

        geom = Geometric(gmean);

        expo = Exponential(emean);

        norm = Normal(nmean, nstd);

        lognorm = Lognormal(logmean, logstd);


        printf(" %3d  %10.6f %4d  %10.6f %10.6f %10.3f\n",
               i, uni, geom, expo, norm, lognorm);
    }

    return 0;
}



/* ===============================================================
   RANDOM NUMBER GENERATION FUNCTIONS
   =============================================================== */



/* ===============================================================
   ASSIGNMENT UPDATE 2
   Correct Uniform Distribution Generator
   =============================================================== */

/* ---------------------------------------------------------------
   Uniform Distribution U(0,1)

   Generates a floating-point number between 0 and 1.

   IMPORTANT CORRECTION:
   ---------------------

   Previous version divided by 2,147,483,647 (MAX_INT).

   However Windows rand() returns values only up to RAND_MAX
   (typically 32767).

   Dividing by MAX_INT produced extremely small values:

        Example:
        rand() = 1000

        1000 / 2147483647 ≈ 0.00000046

   This caused major problems:

   ✔ Normal distribution shifted incorrectly
   ✔ Geometric distribution always returned 1
   ✔ Exponential values incorrect

   Correct Method:

        U = rand() / RAND_MAX

   This produces true U(0,1) values.
   --------------------------------------------------------------- */

double Uniform01()
{
    return (double)rand() / (double)RAND_MAX;
}



/* ---------------------------------------------------------------
   Exponential Distribution

   Uses the Inverse Transform Method:

       X = -μ ln(U)

   where:

       U ~ Uniform(0,1)

   This transforms uniform random numbers into
   exponentially distributed values.
   --------------------------------------------------------------- */

double Exponential(double mu)
{
    double U;

    U = Uniform01();

    return -mu * log(U);
}



/* ---------------------------------------------------------------
   Geometric Distribution

   Generates number of trials until first success.

   Mean = 1/p

   Therefore:

       p = 1/m

   Uses repeated Uniform samples.
   --------------------------------------------------------------- */

int Geometric(double m)
{
    double p;
    int k = 1;

    p = 1.0 / m;

    while(Uniform01() > p)
        k++;

    return k;
}



/* ===============================================================
   Normal Distribution (Box-Muller Method)
   =============================================================== */

/* ---------------------------------------------------------------
   Generates Normal Random Variables.

   Box-Muller Transform:

       Z = sqrt(-2 ln(U1)) cos(2πU2)

   where:

       U1,U2 ~ Uniform(0,1)

   Then:

       X = mean + std*Z
   --------------------------------------------------------------- */

double Normal(float mean, float std)
{
    double U1, U2;
    double Z;

    U1 = Uniform01();
    U2 = Uniform01();

    Z = sqrt(-2.0 * log(U1)) * cos(2 * M_PI * U2);

    return mean + std * Z;
}



/* ---------------------------------------------------------------
   Lognormal Distribution

   If:

       Z ~ Normal(0,1)

   Then:

       X = exp(mean + stdZ)

   is Lognormally distributed.
   --------------------------------------------------------------- */

double Lognormal(float mean, float std)
{
    double Z;

    Z = Normal(0,1);

    return exp(mean + std * Z);
}