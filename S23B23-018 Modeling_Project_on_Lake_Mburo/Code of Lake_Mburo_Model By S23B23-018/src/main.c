#include <stdio.h>
#include <stdlib.h>
#include "sim_config.h"
#include "simulator.h"

// Orchestrator application to run all 16 scenarios
int main() {
    printf("Starting Lake Mburo Entry Gate Simulation...\n");
    printf("==========================================================================================================\n");
    printf("%-8s | %-35s | %-15s | %-15s | %-15s\n", "Lambda", "Service Model", "Mean Delay(min)", "Std Dev(min)", "Utilization(rho)");
    printf("==========================================================================================================\n");
    
    const char* service_names[] = {
        "1: Deterministic (1.5)",
        "2: Exponential (M/M/1)",
        "3: Hyper-Exponential",
        "4: Correlated Exponential"
    };

    for (int i = 0; i < NUM_LAMBDA_SCENARIOS; ++i) {
        double lambda = LAMBDAS[i];
        char arrival_trace_file[256];
        sprintf(arrival_trace_file, "%s%.2f.txt", ARRIVAL_TRACE_PREFIX, lambda);
        
        for (int model = 1; model <= 4; ++model) {
            char service_trace_file[256];
            sprintf(service_trace_file, "%s%d.txt", SERVICE_TRACE_PREFIX, model);
            
            bool is_debug_run = (i == 0 && model == 1);
            if (is_debug_run) {
                // The simulator will automatically print the 10-event manual trace inside execute_simulation
            }
            
            Statistics* simulation_stats = execute_simulation(arrival_trace_file, service_trace_file, is_debug_run);
            
            if (simulation_stats && Statistics_get_count(simulation_stats) == NUM_CARS) {
                // For debug mode, reprint the table header so the formatting doesn't break
                if (is_debug_run) {
                    printf("\n==========================================================================================================\n");
                    printf("%-8s | %-35s | %-15s | %-15s | %-15s\n", "Lambda", "Service Model", "Mean Delay(min)", "Std Dev(min)", "Utilization(rho)");
                    printf("==========================================================================================================\n");
                }
                
                printf("%-8.2f | %-35s | %-15.4f | %-15.4f | %-15.4f\n", 
                    lambda, 
                    service_names[model - 1], 
                    Statistics_get_mean(simulation_stats), 
                    Statistics_get_stddev(simulation_stats),
                    Statistics_get_utilization(simulation_stats));
            } else {
                fprintf(stderr, "Simulation failed or incomplete for lambda %.2f model %d.\n", lambda, model);
                if (simulation_stats) {
                    fprintf(stderr, "Count processed: %d\n", Statistics_get_count(simulation_stats));
                }
            }
            
            Statistics_destroy(simulation_stats);
        }
        printf("----------------------------------------------------------------------------------------------------------\n");
    }
    
    printf("Simulation Automation Complete.\n");
    return 0;
}
