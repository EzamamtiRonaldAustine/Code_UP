#include <stdio.h>
#include <stdlib.h>
#include "simulator.h"

// Simple FIFO queue for cars waiting at the gate.
typedef struct QueueNode {
    double arrival_time;
    struct QueueNode* next;
} QueueNode;

typedef struct {
    QueueNode* head;
    QueueNode* tail;
    int size;
} FIFOQueue;

static void queue_push(FIFOQueue* q, double arr_time) {
    QueueNode* node = (QueueNode*)malloc(sizeof(QueueNode));
    node->arrival_time = arr_time;
    node->next = NULL;
    if (q->tail) {
        q->tail->next = node;
    } else {
        q->head = node;
    }
    q->tail = node;
    q->size++;
}

static double queue_pop(FIFOQueue* q) {
    if (!q->head) return 0.0;
    QueueNode* node = q->head;
    double arrival_time = node->arrival_time;
    q->head = node->next;
    if (!q->head) q->tail = NULL;
    free(node);
    q->size--;
    return arrival_time;
}

static bool queue_is_empty(FIFOQueue* q) {
    return q->size == 0;
}

Statistics* execute_simulation(const char* arrival_trace_path, const char* service_trace_path, bool debug_mode) {
    TraceReader* arrival_reader = TraceIO_open(arrival_trace_path);
    TraceReader* service_reader = TraceIO_open(service_trace_path);
    
    if (!arrival_reader || !service_reader) {
        fprintf(stderr, "Error opening trace files.\n");
        if (arrival_reader) TraceIO_close(arrival_reader);
        if (service_reader) TraceIO_close(service_reader);
        return NULL;
    }
    
    Statistics* statistics = Statistics_create();
    EventQueue* future_event_list = EventQueue_create();
    FIFOQueue waiting_queue = {NULL, NULL, 0};
    
    // System State Variables
    int server_is_busy = 0; // 0 = Idle, 1 = Busy
    double simulation_clock = 0.0;
    double service_start_time = 0.0;
    
    if (debug_mode) {
        printf("\n--- MANUAL VERIFICATION TRACE (First 10 Events) ---\n");
        printf("%-15s | %-15s | %-12s | %-15s\n", "Clock Time", "Event Type", "Queue Length", "Server Status");
        printf("----------------------------------------------------------------------\n");
    }
    
    // Load first inter-arrival time and schedule first arrival
    double next_interarrival_time;
    if (TraceIO_read_next(arrival_reader, &next_interarrival_time)) {
        SimEvent first_arrival = {simulation_clock + next_interarrival_time, EVENT_ARRIVAL, 0};
        EventQueue_insert(future_event_list, first_arrival);
    }
    
    // Main Simulation Loop
    SimEvent current_event;
    int cars_processed = 0;
    int events_printed = 0;
    
    while (EventQueue_pop(future_event_list, &current_event)) {
        simulation_clock = current_event.timestamp;
        
        if (debug_mode && events_printed < 10) {
            printf("%-15.4f | %-15s | %-12d | %-15s\n", 
                simulation_clock, 
                current_event.type == EVENT_ARRIVAL ? "Arrival" : "Departure", 
                waiting_queue.size, 
                server_is_busy ? "Busy" : "Idle");
            events_printed++;
        }
        
        if (current_event.type == EVENT_ARRIVAL) {
            // Schedule the next arrival before handling the current customer.
            if (TraceIO_read_next(arrival_reader, &next_interarrival_time)) {
                SimEvent next_arrival = {simulation_clock + next_interarrival_time, EVENT_ARRIVAL, cars_processed + 1};
                EventQueue_insert(future_event_list, next_arrival);
            }
            
            if (server_is_busy == 0) {
                // Idle server: the car starts service immediately and contributes zero queue delay.
                server_is_busy = 1;
                service_start_time = simulation_clock;
                Statistics_add_sample(statistics, 0.0);
                
                // Read the service duration and place the corresponding departure event in the FEL.
                double service_duration;
                if (TraceIO_read_next(service_reader, &service_duration)) {
                    SimEvent departure = {simulation_clock + service_duration, EVENT_DEPARTURE, cars_processed};
                    EventQueue_insert(future_event_list, departure);
                }
            } else {
                // Busy server: store the arrival time so queue delay can be computed later.
                queue_push(&waiting_queue, simulation_clock);
            }
        } 
        else if (current_event.type == EVENT_DEPARTURE) {
            cars_processed++;
            
            if (queue_is_empty(&waiting_queue)) {
                // No one waiting, so the server becomes idle after this completion.
                server_is_busy = 0;
                Statistics_add_busy_time(statistics, simulation_clock - service_start_time);
            } else {
                // Another car is waiting, so the server remains busy and the next service starts now.
                Statistics_add_busy_time(statistics, simulation_clock - service_start_time);
                service_start_time = simulation_clock;
                
                double start_wait_time = queue_pop(&waiting_queue);
                double queueing_delay = simulation_clock - start_wait_time;
                Statistics_add_sample(statistics, queueing_delay);
                
                // Read the next service duration and schedule the following departure.
                double service_duration;
                if (TraceIO_read_next(service_reader, &service_duration)) {
                    SimEvent departure = {simulation_clock + service_duration, EVENT_DEPARTURE, cars_processed};
                    EventQueue_insert(future_event_list, departure);
                }
            }
        }
    }
    
    if (server_is_busy == 1) {
        Statistics_add_busy_time(statistics, simulation_clock - service_start_time);
    }
    Statistics_set_total_time(statistics, simulation_clock);
    
    // Clean up
    TraceIO_close(arrival_reader);
    TraceIO_close(service_reader);
    EventQueue_destroy(future_event_list);
    
    // Empty whatever remains in queue (should be empty but for memory safety)
    while(!queue_is_empty(&waiting_queue)) { queue_pop(&waiting_queue); }
    
    return statistics;
}
