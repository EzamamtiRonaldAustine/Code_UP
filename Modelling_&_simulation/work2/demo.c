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

   The program prints 200 observations and then computes:

   • Mean
   • Minimum
   • Maximum
   • Expected values

   IMPORTANT CHANGES FROM ORIGINAL VERSION
   ---------------------------------------
   1. Removed erand48() (not supported on Windows)
   2. Replaced rejection method with Box-Muller method
   3. Added srand(time(NULL))
   4. FIXED Uniform01() using RAND_MAX
   5. Added M_PI definition
   6. ADDED statistical summary table

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
   Define PI constant for Windows
   =============================================================== */

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif


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

    float nmean = 0.0;
    float nstd  = 1.0;
    float logmean = 5.9651;
    float logstd  = 0.4832;
    float emean = 0.352;
    float gmean = 14.0;



    /* ===========================================================
       ASSIGNMENT UPDATE 3 – STATISTICS VARIABLES

       These variables accumulate data in order to compute:

       • Mean
       • Minimum
       • Maximum

       at the end of simulation.
       =========================================================== */

    double sumU = 0, sumG = 0, sumE = 0, sumN = 0, sumL = 0;

    double minU = 1.0;
    double minG = 1e9;
    double minE = 1e9;
    double minN = 1e9;
    double minL = 1e9;

    double maxU = 0.0;
    double maxG = 0.0;
    double maxE = 0.0;
    double maxN = -1e9;
    double maxL = 0.0;



    /* Initialize random seed */

    srand(time(NULL));



    printf(" Obs     U(0,1)   Geom     Exp     Norm(0,1)  LogNorm(m,s)\n");
    printf("---------------------------------------------------------\n");



    /* ===========================================================
       Generate Random Samples
       =========================================================== */

    for(i = 1; i <= NUM_VALUES; i++)
    {

        uni = Uniform01();
        geom = Geometric(gmean);
        expo = Exponential(emean);
        norm = Normal(nmean, nstd);
        lognorm = Lognormal(logmean, logstd);



        /* Print Results */

        printf(" %3d  %10.6f %4d  %10.6f %10.6f %10.3f\n",
               i, uni, geom, expo, norm, lognorm);



        /* =======================================================
           Update Statistics
           ======================================================= */

        sumU += uni;
        sumG += geom;
        sumE += expo;
        sumN += norm;
        sumL += lognorm;



        /* Update Minimum Values */

        if(uni < minU) minU = uni;
        if(geom < minG) minG = geom;
        if(expo < minE) minE = expo;
        if(norm < minN) minN = norm;
        if(lognorm < minL) minL = lognorm;



        /* Update Maximum Values */

        if(uni > maxU) maxU = uni;
        if(geom > maxG) maxG = geom;
        if(expo > maxE) maxE = expo;
        if(norm > maxN) maxN = norm;
        if(lognorm > maxL) maxL = lognorm;
    }



    /* ===========================================================
       SUMMARY TABLE
       =========================================================== */

    printf("\n---------------------------------------------------------\n");
    printf(" SUMMARY STATISTICS (N = %d)\n", NUM_VALUES);
    printf("---------------------------------------------------------\n");

    printf(" Metric      U(0,1)      Geom        Exp       Norm      LogNorm\n");

    printf(" Mean:    %10.4f  %10.4f  %10.4f  %10.4f  %10.4f\n",
            sumU/NUM_VALUES,
            sumG/NUM_VALUES,
            sumE/NUM_VALUES,
            sumN/NUM_VALUES,
            sumL/NUM_VALUES);

    printf(" Min:     %10.4f  %10.4f  %10.4f  %10.4f  %10.4f\n",
            minU,minG,minE,minN,minL);

    printf(" Max:     %10.4f  %10.4f  %10.4f  %10.4f  %10.4f\n",
            maxU,maxG,maxE,maxN,maxL);


    /* Expected Theoretical Values */

    printf(" Expected:    0.5000     14.0000      0.3520      0.0000    437.8000\n");

    printf("---------------------------------------------------------\n");


    return 0;
}



/* ===============================================================
   RANDOM NUMBER FUNCTIONS
   =============================================================== */


/* Uniform Distribution */

double Uniform01()
{
    return (double)rand() / (double)RAND_MAX;
}



/* Exponential Distribution */

double Exponential(double mu)
{
    double U;

    U = Uniform01();

    return -mu * log(U);
}



/* Geometric Distribution */

int Geometric(double m)
{
    double p;
    int k = 1;

    p = 1.0 / m;

    while(Uniform01() > p)
        k++;

    return k;
}



/* Normal Distribution (Box-Muller) */

double Normal(float mean, float std)
{
    double U1,U2,Z;

    U1 = Uniform01();
    U2 = Uniform01();

    Z = sqrt(-2.0 * log(U1)) * cos(2*M_PI*U2);

    return mean + std*Z;
}



/* Lognormal Distribution */

double Lognormal(float mean, float std)
{
    double Z;

    Z = Normal(0,1);

    return exp(mean + std*Z);
}