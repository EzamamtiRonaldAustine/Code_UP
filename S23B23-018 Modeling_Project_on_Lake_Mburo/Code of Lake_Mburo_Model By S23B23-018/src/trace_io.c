#include <stdio.h>
#include <stdlib.h>
#include "trace_io.h"

// Concrete definition of the opaque pointer from trace_io.h
struct TraceReader {
    FILE* file;
};

//Tracer IO functions for reading trace files. The TraceReader struct encapsulates the FILE pointer, and the functions provide a simple interface for opening, reading, and closing trace files without exposing the internal details to the rest of the codebase.
TraceReader* TraceIO_open(const char* filepath) {
    FILE* f = fopen(filepath, "r");
    if (!f) {
        return NULL;
    }
    
    TraceReader* reader = (TraceReader*)malloc(sizeof(TraceReader));
    if (!reader) {
        fclose(f);
        return NULL;
    }
    
    reader->file = f;
    return reader;
}

bool TraceIO_read_next(TraceReader* reader, double* out_value) {
    if (!reader || !reader->file) return false;
    
    if (fscanf(reader->file, "%lf", out_value) == 1) {
        return true;
    }
    return false;
}

void TraceIO_close(TraceReader* reader) {
    if (reader) {
        if (reader->file) {
            fclose(reader->file);
        }
        free(reader);
    }
}
