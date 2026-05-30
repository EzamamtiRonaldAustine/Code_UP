#include "rvg.h"
#include <stdlib.h>
#include <math.h>

void RVG_init(unsigned int seed) {
    srand(seed);
}

double RVG_uniform(void) {
    // Generate a uniform random value strictly in (0.0, 1.0].
    // rand() returns 0 to RAND_MAX. +1.0 ensures we never return exactly 0.0 to avoid log(0) error.
    return ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
}

double RVG_exponential(double mean) {
    double uniform_random = RVG_uniform();
    
    // Mathematical Formula (Inverse Transform):
    // x = -mean * ln(U)
    // Converts the uniform probability into an exponential distribution.
    return -mean * log(uniform_random);
}

double RVG_deterministic(double constant_value) {
    return constant_value;
}

double RVG_hyper_exponential(double mean1, double mean2) {
    // Generates a Hyper-Exponential distribution, simulating high variance (e.g., mixed tourist types).
    // Formula: 
    // If U <= 0.5, then x = Exp(mean1)
    // Else, x = Exp(mean2)
    double probability_coin = RVG_uniform();
    
    if (probability_coin <= 0.5) {
        return RVG_exponential(mean1);
    } else {
        return RVG_exponential(mean2);
    }
}

// Generates a correlated exponential using a Bernoulli mixture model.
// The cleanest, mathematical rigorous way to induce a constant positive correlation (rho)
// while perfectly maintaining the Marginal Exponential distribution.
//
// Mathematical Formula:
// S_{i} = S_{i-1} with probability rho, else S_{i} = Exp(mean)
// This guarantees that the sequence has an exact lag-1 autocorrelation of rho.
double RVG_correlated_exponential(double mean, double rho, double* previous_value) {
    double uniform_random = RVG_uniform();
    double current_value;
    
    if (*previous_value >= 0.0 && uniform_random <= rho) {
        // Keep the exact same value to induce positive temporal correlation ("bad luck cluster")
        current_value = *previous_value;
    } else {
        // Generate a new independent exponential value
        current_value = RVG_exponential(mean);
    }
    
    // Save this state so the next generated element can potentially copy it
    *previous_value = current_value;
    return current_value;
}
