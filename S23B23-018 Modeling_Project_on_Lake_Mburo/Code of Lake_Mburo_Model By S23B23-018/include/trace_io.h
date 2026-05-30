#ifndef TRACE_IO_H_
#define TRACE_IO_H_

#include <stdbool.h>
#include "sim_config.h"

/**
 * trace_io.h
 * 
 * Trace I/O module.
 * Responsible for opening, reading, and closing trace files
 * for both arrivals and service times.
 */

// Opaque pointer for Trace Reader state
typedef struct TraceReader TraceReader;

// Open a trace file and return a reader handle. Returns NULL on failure.
TraceReader* TraceIO_open(const char* filepath);

// Read the next double value from the trace. Returns true if successful.
bool TraceIO_read_next(TraceReader* reader, double* out_value);

// Close and free the trace reader.
void TraceIO_close(TraceReader* reader);

#endif // TRACE_IO_H_
