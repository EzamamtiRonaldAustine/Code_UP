
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

  /* -------------------------------------------------------------------------
   * Main simulation loop: Process each job in the input file one by one.
   * The loop continues until end-of-file is reached.
   * ------------------------------------------------------------------------- */
  while (!feof(fp)) {
    index++;                                      /* Increment job counter to track total number of jobs processed */
    
    arrival = GetArrival(fp);                    /* Read the arrival time of the current job from the input file */
    
    /* Calculate delay: If the job arrives before the previous job departs,
     * it must wait in the queue. The delay is the difference between when
     * the previous job departs and when the current job arrives.
     * If arrival >= departure, the server is idle, so no delay occurs. */
    if (arrival < departure) 
      delay = departure - arrival;                /* Job must wait in queue: server is busy */
    else 
      delay = 0.0;                                /* No delay: server was idle, job starts immediately */
    
    service = GetService(fp);                    /* Read the service time (processing duration) for current job */
    
    wait = delay + service;                      /* Total time in system = waiting time in queue + service time */
    
    departure = arrival + wait;                  /* Calculate the time when this job will leave the server */
    
    /* Accumulate statistics for computing averages at the end of simulation */
    sum.delay += delay;                           /* Sum of all queue delays */
    sum.wait += wait;                            /* Sum of all wait times (delay + service) */
    sum.service += service;                      /* Sum of all service times */
  }
  
  /* Calculate total interarrival time: difference between last arrival and simulation start time.
   * This is used to compute the average interarrival time in the output. */
  sum.interarrival = arrival - START;

  printf("\nfor %ld jobs\n", index);
  printf("   average interarrival time = %6.2f\n", sum.interarrival / index);
  printf("   average service time .... = %6.2f\n", sum.service / index);
  printf("   average delay ........... = %6.2f\n", sum.delay / index);
  printf("   average wait ............ = %6.2f\n", sum.wait / index);

  fclose(fp);
  return (0);
}