#include <stdio.h>
#include <stdlib.h>
#include "sim_config.h"
#include "rvg.h"

// Generate arrival traces for different lambdas
void generate_arrival_traces() {
    for (int i = 0; i < NUM_LAMBDA_SCENARIOS; ++i) {
        double lambda = LAMBDAS[i];
        char filename[256];
        sprintf(filename, "%s%.2f.txt", ARRIVAL_TRACE_PREFIX, lambda);
        
        FILE* output_file = fopen(filename, "w");
        if (!output_file) {
            fprintf(stderr, "Error opening %s for writing.\n", filename);
            exit(1);
        }
        
        // Inter-arrival times follow an exponential distribution with mean 1 / lambda.
        double mean_interarrival = 1.0 / lambda;
        for (int sample_index = 0; sample_index < NUM_CARS; ++sample_index) {
            double interarrival_time = RVG_exponential(mean_interarrival);
            fprintf(output_file, "%f\n", interarrival_time);
        }
        fclose(output_file);
        printf("Generated %s\n", filename);
    }
}

// Generate service traces for the 4 specific models
void generate_service_traces() {
    for (int model = 1; model <= 4; ++model) {
        char filename[256];
        sprintf(filename, "%s%d.txt", SERVICE_TRACE_PREFIX, model);
        
        FILE* output_file = fopen(filename, "w");
        if (!output_file) {
            fprintf(stderr, "Error opening %s for writing.\n", filename);
            exit(1);
        }
        
        // Reused by the correlated-exponential generator to preserve lag-1 dependence.
        double previous_correlated_value = -1.0;
        
        for (int sample_index = 0; sample_index < NUM_CARS; ++sample_index) {
            double service_time = 0.0;
            switch(model) {
                case SERVICE_DETERMINISTIC:
                    service_time = RVG_deterministic(DETERMINISTIC_SERVICE_MINUTES);
                    break;
                case SERVICE_EXPONENTIAL:
                    service_time = RVG_exponential(EXPONENTIAL_MEAN_MINUTES);
                    break;
                case SERVICE_HYPER_EXPONENTIAL:
                    service_time = RVG_hyper_exponential(HYPER_EXP_MEAN_1_MINUTES, HYPER_EXP_MEAN_2_MINUTES);
                    break;
                case SERVICE_CORRELATED_EXPONENTIAL:
                    service_time = RVG_correlated_exponential(CORRELATED_EXP_MEAN_MINUTES, CORRELATED_EXP_CORRELATION, &previous_correlated_value);
                    break;
            }
            fprintf(output_file, "%f\n", service_time);
        }
        fclose(output_file);
        printf("Generated %s\n", filename);
    }
}

int main() {
    RVG_init(42); // Deterministic seed for reproducible traces
    printf("Starting trace generation...\n");
    generate_arrival_traces();
    generate_service_traces();
    printf("Trace generation complete.\n");
    return 0;
}
