#ifndef STATISTICS_H_
#define STATISTICS_H_

/**
 * statistics.h
 * 
 * Accumulates delays and computes mean and standard deviation.
 * Uses Welford's online algorithm for stable variance calculation.
 */

// Opaque pointer for Statistics tracker
typedef struct Statistics Statistics;

// Create a new statistics tracker
Statistics* Statistics_create(void);

// Add a delay sample to the running statistics
void Statistics_add_sample(Statistics* stats, double delay);

// Add server busy time to track utilization
void Statistics_add_busy_time(Statistics* stats, double busy_time);

// Set the total simulation clock time for utilization calculation
void Statistics_set_total_time(Statistics* stats, double total_time);

// Get the computed Mean
double Statistics_get_mean(const Statistics* stats);

// Get the computed Standard Deviation
double Statistics_get_stddev(const Statistics* stats);

// Get the Server Utilization (rho)
double Statistics_get_utilization(const Statistics* stats);

// Get the number of samples collected
int Statistics_get_count(const Statistics* stats);

// Destroy the statistics tracker
void Statistics_destroy(Statistics* stats);

#endif // STATISTICS_H_
