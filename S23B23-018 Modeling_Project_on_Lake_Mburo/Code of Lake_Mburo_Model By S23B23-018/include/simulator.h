#ifndef SIMULATOR_H_
#define SIMULATOR_H_

#include "event_queue.h"
#include "trace_io.h"
#include "statistics.h"

/**
 * simulator.h
 * 
 * The Discrete-Event Simulation Engine.
 * Responsible for advancing the clock and executing Event-Scheduling Logic.
 */

// Runs a single trace-driven simulation experiment for a specific lambda and service model.
// Returns the populated Statistics tracker (caller must free it via Statistics_destroy).
// If debug_mode is true, prints a manual trace table of the first 10 events.
Statistics* execute_simulation(const char* arrival_trace_path, const char* service_trace_path, bool debug_mode);

#endif // SIMULATOR_H_
