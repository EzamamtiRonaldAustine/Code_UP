
/* -------------------------------------------------------------------------
 * This program simulates a single-server FIFO service node using arrival
 * times and service times read from a text file.  The server is assumed
 * to be idle when the first job arrives.  All jobs are processed completely
 * so that the server is again idle at the end of the simulation.   The
 * output statistics are the average interarrival time, average service
 * time, the average delay in the queue, and the average wait in the service 
 * node. 
 *
 * Name              : ssq1.c  (Single Server Queue, version 1)
 * Authors           : 
 * Language          : ANSI C
 * Latest Revision   : 
 * Compile with      : gcc ssq1.c 
 * ------------------------------------------------------------------------- 
 */

#include <stdio.h>                              

/* CHANGE: Updated filename to match the actual file 'ssq1 dat.txt' on disk */
#define FILENAME   "ssq1 dat.txt"                  /* input data file */
#define START      0.0

/* =========================== */
   double GetArrival(FILE *fp)                 /* read an arrival time */
/* =========================== */
{ 
  double a;

  fscanf(fp, "%lf", &a);
  return (a);
}

/* =========================== */
   double GetService(FILE *fp)                 /* read a service time */
/* =========================== */
{ 
  double s;

  fscanf(fp, "%lf\n", &s);
  return (s);
}

/* ============== */
   int main(void)
/* ============== */
{
  FILE   *fp;                                  /* input data file      */
  long   index     = 0;                        /* job index            */
  double arrival   = START;                    /* arrival time         */
  double delay;                                /* delay in queue       */
  double service;                              /* service time         */
  double wait;                                 /* delay + service      */
  double departure = START;                    /* departure time       */
  struct {                                     /* sum of ...           */
    double delay;                              /*   delay times        */
    double wait;                               /*   wait times         */
    double service;                            /*   service times      */
    double interarrival;                       /*   interarrival times */
  } sum = {0.0, 0.0, 0.0};

  fp = fopen(FILENAME, "r");
  if (fp == NULL) {
    fprintf(stderr, "Cannot open input file %s\n", FILENAME);
    return (1);
  }

  /* CHANGE: Use fscanf return check instead of feof() for robust loop termination */
  /* Logic: Read arrival and service pairs from file until EOF */
  while (fscanf(fp, "%lf %lf", &arrival, &service) == 2) {
    index++;
    /* Logic: Calculate delay based on whether the server is idle or busy */
    if (arrival < departure) 
      delay      = departure - arrival;        /* Job arrives while previous job is processing */
    else 
      delay      = 0.0;                        /* Server is idle upon arrival */
    wait         = delay + service;            /* Total time in system */
    departure    = arrival + wait;             /* Timestamp of departure */
    sum.delay   += delay;
    sum.wait    += wait;
    sum.service += service;
  }
  sum.interarrival = arrival - START;

  printf("\nfor %ld jobs\n", index);
  printf("   average interarrival time = %6.2f\n", sum.interarrival / index);
  printf("   average service time .... = %6.2f\n", sum.service / index);
  printf("   average delay ........... = %6.2f\n", sum.delay / index);
  printf("   average wait ............ = %6.2f\n", sum.wait / index);

  fclose(fp);
  return (0);
}