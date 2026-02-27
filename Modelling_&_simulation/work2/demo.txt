/* This program demonstrates random numbers generated from       */
/* geometric, exponential, normal, and log normal distributions. */

/* Usage: cc -o demo demo.c -lm                                  */
/*        demo                                                   */

#include <stdio.h>
#include <stdlib.h>
#include <math.h> /* use man 3 log for the math functions */

#define NUM_VALUES 20 /* number of samples to generate */

double ceil(double x);
double erand48(unsigned short []); 
double Uniform01();
double Normal(float, float); 
double Lognormal(float, float);
double Exponential(double);
int Geometric(double);

/* array used for initializing seeds for Normal distribution */
unsigned short Nvar1_seed[3] = {4,7,2};
unsigned short Nvar2_seed[3] = {5,8,1};
unsigned short Nvar3_seed[3] = {9,6,3};

/* array used for initializing seeds for Exponential distribution */
unsigned short Evar1_seed[3] = {2,5,7};
unsigned short Evar2_seed[3] = {3,1,7}; 

main(int argc, char *argv[])
{
  FILE *datafile;
  double white_noise;
  int i, geom;
  float nmean, nstd, logmean, logstd, emean, gmean;
  double norm, lognorm, expo, uni;

  /* choose your own values for these next six variables if you wish */

  /* mean for geometric distribution is 1/p */
  gmean = 14.0; /* example: mean scene duration in Oz MPEG video trace */

  /* mean for exponential distribution */
  emean = 0.352;   /* example: mean on time in seconds */

  /* mean for Normal distribution */
  nmean = 0.0;   /* example: mean for N(0,1) distribution */

  /* standard deviation for Normal distribution */
  nstd = 1.0;    /* example: std dev for N(0,1) distribution */

  /* mean for lognormal distribution */
  logmean = 5.9651; /* example: mean size of I frames in Oz MPEG video */

  /* standard deviation for lognormal distribution */
  logstd = 0.4832;  /* example: std dev for I frames in Oz MPEG video */

  printf(" Obs     U(0,1)   Geom     Exp     Norm(0,1)  LogNorm(m,s)\n");
  printf("---------------------------------------------------------\n");

  for(i = 1; i <= NUM_VALUES; i++)
    {
      /* generate a value from a uniform distribution */
      uni = Uniform01();

      /* generate a value from a geometric distribution */
      geom = Geometric(gmean);

      /* generate a value from an exponential distribution */
      expo = Exponential(emean);

      /* generate a value from a normal distribution */
      norm = Normal(nmean, nstd);   

      /* generate a value from a normal distribution */
      lognorm = Lognormal(logmean, logstd);

      /* print them all out */
      printf(" %3d  %10.6f %4d  %10.6f %10.6f %10.3f\n",
	     i, uni, geom, expo, norm, lognorm);

    } /* end of for loop */
} /* end of main */

/***********************************************************************/
/*                 RANDOM NUMBER GENERATION STUFF                      */
/***********************************************************************/

/* Parameters for random number generation. */
#define MAX_INT 2147483647       /* Maximum positive integer 2^31 - 1 */

/* Generate a random floating point number uniformly distributed in [0,1] */
double Uniform01()
  {
    double randnum;
    /* get a random positive integer from random() */
    randnum = (double) 1.0 * random();
    /* divide by max int to get something in 0..1  */
    randnum = (float) randnum / (1.0 * MAX_INT); 
    return( randnum );
  }

/* Generate a random floating point number from an exponential    */
/* distribution with mean mu.                                     */

double Exponential(mu)
    double mu;
 {
    double randnum, ans;

    randnum = Uniform01();
    ans = -(mu) * log(randnum);
    return( ans );
  }

/* Generate random positive integer geometrically distributed with mean m */
int Geometric(m)
    double m;
  {
    double p;    /* p is the probability of "success" for each trial */
    int k;

    k = 1;
    p = 1.0 / m;                          /* the inverse of the mean */
    while( Uniform01() > p )
      k++;
    return( k );
  }

/* the rejection method is used for normal distribution 
   (a) Generate two uniform U(0,1) variates u1 and u2. 
   (b) Let x = -log(u1).
   (c) If u2 > e to the power -(x - 1)square by 2, go back to step
   [a].
   (d) Generate u3.
   (e) If u3 > 0.5, return (mean + (std * x)); otherwise return
   (mean - (std * x)). */

double Normal(float mean, float std)
{
  double var_u1, var_u2, var_u3;
  double x, tmp_val;
  
  var_u1 = erand48(Nvar1_seed);
  var_u2 = erand48(Nvar2_seed);
  x = -log(var_u1);
  tmp_val = exp(-((x - 1)*(x - 1)) / 2);
  while(var_u2 > tmp_val)
    {
      var_u1 = erand48(Nvar1_seed);
      var_u2 = erand48(Nvar2_seed);
      x = -log(var_u1);
      tmp_val = exp(-((x - 1)*(x - 1)) / 2);
    }
  var_u3 = erand48(Nvar3_seed);
  if(var_u3 > 0.5)
    return(mean + (std * x));
  else 
    return(mean - (std * x));
}

double Lognormal(float mean, float std)
{
  double lognormal_x, tmp_var;
  
  lognormal_x = Normal(0,1);
  tmp_var = mean + (std * lognormal_x);
  return(exp(tmp_var));
}
