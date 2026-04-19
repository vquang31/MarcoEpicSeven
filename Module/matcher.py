from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from Module.assets import Template
from Module.geometry import MatchResult, Rect


@dataclass(frozen=True)
class SearchArea:
    image: np.ndarray
    offset_x: int = 0
    offset_y: int = 0


class TemplateMatcher:
    def __init__(self, scale_values: tuple[float, ...]) -> None:
        self.scale_values = scale_values

    def find_best(
        self,
        search_image: np.ndarray,
        template: Template,
        threshold: float,
        offset_x: int = 0,
        offset_y: int = 0,
    ) -> MatchResult | None:
        search_gray = cv2.cvtColor(search_image, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template.image, cv2.COLOR_BGR2GRAY)
        best: MatchResult | None = None

        for scale in self.scale_values:
            scaled = cv2.resize(
                template_gray,
                dsize=None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC,
            )
            height, width = scaled.shape[:2]
            if width < 8 or height < 8:
                continue
            if width > search_gray.shape[1] or height > search_gray.shape[0]:
                continue

            result = cv2.matchTemplate(search_gray, scaled, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val < threshold:
                continue

            match = MatchResult(
                name=template.name,
                confidence=float(max_val),
                rect=Rect(
                    left=max_loc[0] + offset_x,
                    top=max_loc[1] + offset_y,
                    width=width,
                    height=height,
                ),
            )
            if best is None or match.confidence > best.confidence:
                best = match
        return best

