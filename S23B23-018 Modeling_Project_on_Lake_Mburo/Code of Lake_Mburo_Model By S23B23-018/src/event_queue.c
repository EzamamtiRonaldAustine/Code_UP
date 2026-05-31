#include <stdlib.h>
#include "event_queue.h"

// Node for a singly-linked sorted list
typedef struct EventNode {
    SimEvent event;
    struct EventNode* next;
} EventNode;

// Concrete definition of the opaque EventQueue pointer
struct EventQueue {
    EventNode* head;
    int size;
};

// Creates a new event queue
EventQueue* EventQueue_create(void) {
    EventQueue* eq = (EventQueue*)malloc(sizeof(EventQueue));
    if (eq) {
        eq->head = NULL;
        eq->size = 0;
    }
    return eq;
}

// Inserts an event into the queue in sorted order
void EventQueue_insert(EventQueue* eq, SimEvent event) {
    if (!eq) return;
    
    EventNode* new_node = (EventNode*)malloc(sizeof(EventNode));
    if (!new_node) return;
    
    new_node->event = event;
    new_node->next = NULL;
    
    // Insert in sorted order (ascending by timestamp)
    if (eq->head == NULL || event.timestamp < eq->head->event.timestamp) {
        new_node->next = eq->head;
        eq->head = new_node;
    } else {
        EventNode* current = eq->head;
        while (current->next != NULL && current->next->event.timestamp <= event.timestamp) {
            current = current->next;
        }
        new_node->next = current->next;
        current->next = new_node;
    }
    eq->size++;
}

// Pops the next event from the queue (the one with the smallest timestamp)
bool EventQueue_pop(EventQueue* eq, SimEvent* out_event) {
    if (EventQueue_is_empty(eq)) {
        return false;
    }
    
    EventNode* temp = eq->head;
    *out_event = temp->event;
    
    eq->head = temp->next;
    free(temp);
    eq->size--;
    
    return true;
}

// Checks if the event queue is empty
bool EventQueue_is_empty(const EventQueue* eq) {
    return (eq == NULL || eq->head == NULL);
}

// Destroys the event queue and frees all associated memory
void EventQueue_destroy(EventQueue* eq) {
    if (!eq) return;
    
    EventNode* current = eq->head;
    while (current != NULL) {
        EventNode* next = current->next;
        free(current);
        current = next;
    }
    free(eq);
}
