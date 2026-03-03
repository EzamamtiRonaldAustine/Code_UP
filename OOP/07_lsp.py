"""
Week 4 – Object-Oriented Design
Code Example 07: Liskov Substitution Principle

A subclass must be able to replace its base class without breaking
the code that uses the base class.
"""

from abc import ABC, abstractmethod


# ─── BEFORE: LSP Violation ────────────────────────────────────────────────────

class Bird_BAD:
    def fly(self):
        print(f"{self.__class__.__name__} is flying")


class Penguin_BAD(Bird_BAD):
    def fly(self):
        raise NotImplementedError("Penguins cannot fly")


def make_bird_fly(bird: Bird_BAD):
    """
    This function was written to work with any Bird.
    It will CRASH if given a Penguin.
    Penguin is not a substitutable Bird in this context.
    """
    bird.fly()


# make_bird_fly(Penguin_BAD())  # RuntimeError: Penguins cannot fly
#
# The LSP diagnostic: would you ever need to write isinstance(bird, Penguin)?
# If yes, the hierarchy is broken.


# ─── AFTER: LSP Applied ───────────────────────────────────────────────────────

class Bird(ABC):
    """
    A Bird promises only what ALL birds can do.
    fly() is not in that list — not all birds fly.
    """
    @abstractmethod
    def move(self) -> None:
        """All birds can move. How they move varies."""
        pass

    @abstractmethod
    def make_sound(self) -> str:
        pass


class FlyingBird(Bird, ABC):
    """Specialisation for birds that fly."""
    def move(self) -> None:
        print(f"{self.__class__.__name__} is flying")


class SwimmingBird(Bird, ABC):
    """Specialisation for birds that swim."""
    def move(self) -> None:
        print(f"{self.__class__.__name__} is swimming")


class Eagle(FlyingBird):
    def make_sound(self) -> str:
        return "screech"


class Penguin(SwimmingBird):
    def make_sound(self) -> str:
        return "squawk"


def observe_bird(bird: Bird):
    """
    Works with ANY Bird. Will never crash.
    Every Bird can move and make a sound — LSP is satisfied.
    """
    bird.move()
    print(f"It says: {bird.make_sound()}")


if __name__ == "__main__":
    observe_bird(Eagle())
    observe_bird(Penguin())    # no crash — Penguin is now a proper Bird
