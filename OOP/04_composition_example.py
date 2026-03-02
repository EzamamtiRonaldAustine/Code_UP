"""
Week 4 – Object-Oriented Design
Code Example 04: Composition vs Inheritance (Notification System)

Shows how composition handles variations that would cause
a combinatorial explosion with inheritance.
"""

from abc import ABC, abstractmethod


# ── The abstraction (the "contract") ──────────────────────────────────────────

class NotificationChannel(ABC):
    """
    Abstract base class defining what every notification channel must do.
    This is the abstraction that both the service and the implementations depend on.
    """
    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        pass


# ── Concrete implementations ───────────────────────────────────────────────────

class EmailChannel(NotificationChannel):
    def send(self, recipient: str, message: str) -> None:
        print(f"[EMAIL  → {recipient}] {message}")


class SMSChannel(NotificationChannel):
    def send(self, recipient: str, message: str) -> None:
        print(f"[SMS    → {recipient}] {message}")


class WhatsAppChannel(NotificationChannel):
    """
    Adding WhatsApp = writing ONE new class.
    NotificationService does not change.
    EmailChannel does not change.
    SMSChannel does not change.
    """
    def send(self, recipient: str, message: str) -> None:
        print(f"[WHATSAPP → {recipient}] {message}")


# ── The service — composed, not inherited ─────────────────────────────────────

class NotificationService:
    """
    Does not extend or inherit from any channel.
    Has a collection of channels — assembled at construction time.

    This is dependency inversion in action:
    NotificationService depends on the NotificationChannel abstraction,
    not on any concrete EmailChannel or SMSChannel.
    """

    def __init__(self, channels: list[NotificationChannel]) -> None:
        if not channels:
            raise ValueError("At least one notification channel is required.")
        self._channels = channels

    def notify(self, recipient: str, message: str) -> None:
        for channel in self._channels:
            channel.send(recipient, message)


# ── Usage — behaviour assembled at runtime ─────────────────────────────────────

if __name__ == "__main__":
    print("=== Email only ===")
    service = NotificationService([EmailChannel()])
    service.notify("alice@ucu.ac.ug", "Welcome to the course!")

    print("\n=== Email + SMS ===")
    service = NotificationService([EmailChannel(), SMSChannel()])
    service.notify("bob@ucu.ac.ug", "Assignment due tomorrow.")

    print("\n=== All three channels ===")
    service = NotificationService([EmailChannel(), SMSChannel(), WhatsAppChannel()])
    service.notify("carol@ucu.ac.ug", "Exam results are out.")
