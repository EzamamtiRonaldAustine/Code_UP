"""
Week 4 – Object-Oriented Design
Code Example 08: Interface Segregation Principle

Don't force a class to depend on methods it doesn't use.
The diagnostic: implementing a method with 'pass' because you don't need it.
"""

from abc import ABC, abstractmethod


# ─── BEFORE: ISP Violation ────────────────────────────────────────────────────

class Worker_BAD(ABC):
    """
    A fat interface. Mixes human and robot concerns.
    Robots are forced to implement eat() — which makes no sense.
    """
    @abstractmethod
    def work(self): pass

    @abstractmethod
    def eat(self): pass

    @abstractmethod
    def attend_meeting(self): pass


class RobotWorker_BAD(Worker_BAD):
    def work(self):
        print("Robot: working")

    def eat(self):
        pass                    # ← forced nonsense — this is the ISP smell

    def attend_meeting(self):
        pass                    # ← also forced nonsense


# ─── AFTER: ISP Applied ───────────────────────────────────────────────────────

class Workable(ABC):
    """Everything that can work implements this."""
    @abstractmethod
    def work(self) -> None: pass


class Feedable(ABC):
    """Only beings that need food implement this."""
    @abstractmethod
    def eat(self) -> None: pass


class MeetingAttendee(ABC):
    """Only entities that attend meetings implement this."""
    @abstractmethod
    def attend_meeting(self) -> None: pass


class RobotWorker(Workable):
    """
    A robot only implements what it actually does.
    No forced nonsense. No empty pass blocks.
    """
    def work(self) -> None:
        print("Robot: processing task")


class HumanWorker(Workable, Feedable, MeetingAttendee):
    """
    A human implements all three — because a human genuinely does all three.
    """
    def work(self) -> None:
        print("Human: working on feature")

    def eat(self) -> None:
        print("Human: having lunch")

    def attend_meeting(self) -> None:
        print("Human: in standup")


# ── Testing substitutability ───────────────────────────────────────────────────
def run_work_shift(workers: list[Workable]) -> None:
    """Only cares about work. Doesn't know or care about eating."""
    for w in workers:
        w.work()


if __name__ == "__main__":
    run_work_shift([RobotWorker(), HumanWorker()])
