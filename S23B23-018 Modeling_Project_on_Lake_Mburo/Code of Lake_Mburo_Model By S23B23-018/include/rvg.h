#ifndef RVG_H_
#define RVG_H_

/**
 * rvg.h
 * 
 * Random Variate Generation module.
 * Implements the Inverse Transform Method for various distributions
 * 
 */

// Initialize the random number sequence
void RVG_init(unsigned int seed);

// Generate a Uniform(0,1) variate
double RVG_uniform(void);

// Generate an Exponential variate with a given mean
double RVG_exponential(double mean);

// Generate a Deterministic variate (always returns constant_value)
double RVG_deterministic(double constant_value);

// Generate a Hyper-exponential variate with 50/50 probability between two means
double RVG_hyper_exponential(double mean1, double mean2);

// Generate a Correlated Exponential variate
// (Uses a simple moving average auto-regressive AR(1) model technique to induce positive correlation)
double RVG_correlated_exponential(double mean, double rho, double* previous_exponential_std_uniform);

#endif // RVG_H_
