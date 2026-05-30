#ifndef SIM_CONFIG_H_
#define SIM_CONFIG_H_

/**
 * sim_config.h
 *
 * Centralized configuration to eliminate magic numbers.
 * Defines project requirements (e.g. 10,000 cars),
 * lambda variations, and service time parameters.
 */

// General Simulation Requirements
#define NUM_CARS 10000

// Service distribution model identifiers
typedef enum {
    SERVICE_DETERMINISTIC = 1,
    SERVICE_EXPONENTIAL = 2,
    SERVICE_HYPER_EXPONENTIAL = 3,
    SERVICE_CORRELATED_EXPONENTIAL = 4
} ServiceModel;

// Model specific parameters (Constants from the assignment)
#define DETERMINISTIC_SERVICE_MINUTES 1.5
#define EXPONENTIAL_MEAN_MINUTES 1.5

#define HYPER_EXP_MEAN_1_MINUTES 1.0
#define HYPER_EXP_MEAN_2_MINUTES 2.0
#define HYPER_EXP_PROBABILITY 0.5

#define CORRELATED_EXP_MEAN_MINUTES 1.5
#define CORRELATED_EXP_CORRELATION 0.2

// Lambdas to evaluate
#define NUM_LAMBDA_SCENARIOS 4
extern const double LAMBDAS[NUM_LAMBDA_SCENARIOS];

// File naming configurations
// Trace files will be generated as "arrivals_X.XX.txt" and "services_model_Y.txt"
#define ARRIVAL_TRACE_PREFIX "traces/arrivals_"
#define SERVICE_TRACE_PREFIX "traces/services_model_"

#endif // SIM_CONFIG_H_
