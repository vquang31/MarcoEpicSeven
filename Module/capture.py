from __future__ import annotations

from dataclasses import dataclass

import cv2
import mss
import numpy as np

from Module.geometry import Rect


@dataclass(frozen=True)
class Frame:
    image: np.ndarray
    width: int
    height: int


class ScreenCapture:
    def __init__(self) -> None:
        self._mss = mss.mss()

    def grab(self) -> Frame:
        monitor = self._mss.monitors[0]
        raw = np.array(self._mss.grab(monitor))
        bgr = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)
        height, width = bgr.shape[:2]
        return Frame(image=bgr, width=width, height=height)

    @staticmethod
    def crop(image: np.ndarray, rect: Rect) -> np.ndarray:
        return image[rect.top : rect.bottom, rect.left : rect.right].copy()
