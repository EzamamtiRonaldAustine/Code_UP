#ifndef EVENT_QUEUE_H_
#define EVENT_QUEUE_H_

#include <stdbool.h>
#include <stdint.h>

/**
 * event_queue.h
 * 
 * Future Event List (FEL) Management.
 * Implemented as a Priority Queue ordered by event timestamp.
 */

// Event types for the simulation
typedef enum {
    EVENT_ARRIVAL = 0,
    EVENT_DEPARTURE = 1
} EventType;

// Event structure
typedef struct {
    double timestamp;  // The simulation clock time when this event occurs
    EventType type;    // The type of the event
    int entity_id;     // Optional: ID of the car/driver (useful for tracking specific delays)
} SimEvent;

// Opaque pointer for the Event Queue (Priority Queue)
typedef struct EventQueue EventQueue;

// Initialize a new Event Queue
EventQueue* EventQueue_create(void);

// Insert a new event into the FEL (sorted by timestamp)
void EventQueue_insert(EventQueue* eq, SimEvent event);

// Remove and return the event with the earliest timestamp
// Returns true if an event was popped, false if the queue is empty
bool EventQueue_pop(EventQueue* eq, SimEvent* out_event);

// Check if the Event Queue is empty
bool EventQueue_is_empty(const EventQueue* eq);

// Destroy the Event Queue and free memory
void EventQueue_destroy(EventQueue* eq);

#endif // EVENT_QUEUE_H_
