#include <stdlib.h>
#include <math.h>
#include "statistics.h"

// Concrete implementation of Statistics
struct Statistics {
    int count;                  // Total number of tourists processed
    double mean;                // Running average of delay (minutes)
    double sum_squared_diffs;   // M2 component for Welford's algorithm (sum of squared differences from the mean)
    double total_busy_time;     // Cumulative time the ranger was ticketing
    double total_simulation_duration; // Final clock timestamp
};

Statistics* Statistics_create(void) {
    Statistics* stats = (Statistics*)malloc(sizeof(Statistics));
    if (stats) {
        stats->count = 0;
        stats->mean = 0.0;
        stats->sum_squared_diffs = 0.0;
        stats->total_busy_time = 0.0;
        stats->total_simulation_duration = 0.0;
    }
    return stats;
}

void Statistics_add_sample(Statistics* stats, double delay) {
    if (!stats) return;
    
    // Welford's Algorithm: Mathematically robust way to compute rolling mean and variance
    // without suffering from floating-point overflow or precision loss for large datasets.
    stats->count += 1;
    double delta = delay - stats->mean;
    stats->mean += delta / stats->count;
    double delta2 = delay - stats->mean;
    
    // Update M2 (Sum of Squared Differences)
    stats->sum_squared_diffs += delta * delta2;
}

void Statistics_add_busy_time(Statistics* stats, double busy_time) {
    if (stats) stats->total_busy_time += busy_time;
}

void Statistics_set_total_time(Statistics* stats, double total_time) {
    if (stats) stats->total_simulation_duration = total_time;
}

double Statistics_get_mean(const Statistics* stats) {
    if (!stats || stats->count == 0) return 0.0;
    return stats->mean;
}

double Statistics_get_stddev(const Statistics* stats) {
    if (!stats || stats->count < 2) return 0.0;
    
    // Variance = M2 / (n - 1)
    double variance = stats->sum_squared_diffs / (stats->count - 1);
    return sqrt(variance);
}

double Statistics_get_utilization(const Statistics* stats) {
    if (!stats || stats->total_simulation_duration == 0.0) return 0.0;
    return stats->total_busy_time / stats->total_simulation_duration;
}

int Statistics_get_count(const Statistics* stats) {
    if (!stats) return 0;
    return stats->count;
}

void Statistics_destroy(Statistics* stats) {
    if (stats) {
        free(stats);
    }
}
