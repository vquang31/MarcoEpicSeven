from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class Rect:
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    @property
    def center(self) -> Point:
        return Point(self.left + self.width // 2, self.top + self.height // 2)

    def clamp(self, max_width: int, max_height: int) -> "Rect":
        left = max(0, min(self.left, max_width))
        top = max(0, min(self.top, max_height))
        right = max(left, min(self.right, max_width))
        bottom = max(top, min(self.bottom, max_height))
        return Rect(left, top, right - left, bottom - top)

    def translate(self, dx: int, dy: int) -> "Rect":
        return Rect(self.left + dx, self.top + dy, self.width, self.height)


@dataclass(frozen=True)
class MatchResult:
    name: str
    confidence: float
    rect: Rect

