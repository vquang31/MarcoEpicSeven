from __future__ import annotations

from dataclasses import dataclass

from Module.assets import AssetBundle
from Module.config import BotConfig
from Module.geometry import MatchResult, Point, Rect
from Module.matcher import TemplateMatcher
import logging


LOGGER = logging.getLogger("secret_shop_bot")


@dataclass(frozen=True)
class SceneContext:
    frame_rect: Rect
    refresh_button: MatchResult
    scroll_start: Point
    scroll_end: Point


class SceneLocator:
    def __init__(self, assets: AssetBundle, matcher: TemplateMatcher, config: BotConfig) -> None:
        self.assets = assets
        self.matcher = matcher
        self.config = config

    def locate(self, screen_image, screen_width: int, screen_height: int) -> SceneContext | None:
        left_match = self.matcher.find_best(
            screen_image,
            self.assets.top_left,
            self.config.match.scene_threshold,
        )
        if left_match is None:
            LOGGER.debug("Khong tim thay image_TopLeft.png tren man hinh hien tai.")
            return None
        LOGGER.info(
            "Detect thanh cong image_TopLeft.png | conf=%.3f | rect=(%s, %s, %s, %s)",
            left_match.confidence,
            left_match.rect.left,
            left_match.rect.top,
            left_match.rect.width,
            left_match.rect.height,
        )

        top_left_anchor_x = left_match.rect.left
        top_left_anchor_y = left_match.rect.top

        right_search_rect = Rect(
            left=left_match.rect.right,
            top=max(0, left_match.rect.top - 20),
            width=max(1, screen_width - left_match.rect.right),
            height=max(
                left_match.rect.height + 60,
                min(screen_height - max(0, left_match.rect.top - 20), left_match.rect.height * 2),
            ),
        ).clamp(screen_width, screen_height)
        right_search_image = screen_image[
            right_search_rect.top : right_search_rect.bottom,
            right_search_rect.left : right_search_rect.right
        ]
        right_match = self.matcher.find_best(
            right_search_image,
            self.assets.top_right,
            self.config.match.scene_threshold,
            offset_x=right_search_rect.left,
            offset_y=right_search_rect.top,
        )
        if right_match is None:
            LOGGER.debug(
                "Da tim thay image_TopLeft.png nhung khong tim thay image_TopRight.png trong vung (%s, %s, %s, %s).",
                right_search_rect.left,
                right_search_rect.top,
                right_search_rect.width,
                right_search_rect.height,
            )
            return None
        LOGGER.info(
            "Detect thanh cong image_TopRight.png | conf=%.3f | rect=(%s, %s, %s, %s)",
            right_match.confidence,
            right_match.rect.left,
            right_match.rect.top,
            right_match.rect.width,
            right_match.rect.height,
        )

        frame_width = right_match.rect.right - top_left_anchor_x
        if frame_width <= 0:
            LOGGER.debug(
                "Frame width khong hop le. right=%s left=%s",
                right_match.rect.right,
                top_left_anchor_x,
            )
            return None
        frame_height = int(round(frame_width * self.config.scene_aspect_height / self.config.scene_aspect_width))
        frame_rect = Rect(
            left=top_left_anchor_x,
            top=top_left_anchor_y,
            width=frame_width,
            height=frame_height,
        ).clamp(screen_width, screen_height)

        frame_image = screen_image[frame_rect.top : frame_rect.bottom, frame_rect.left : frame_rect.right]
        refresh_match = self.matcher.find_best(
            frame_image,
            self.assets.refresh_button,
            self.config.match.button_threshold,
            offset_x=frame_rect.left,
            offset_y=frame_rect.top,
        )
        if refresh_match is None:
            LOGGER.debug(
                "Da xac dinh frame=(%s, %s, %s, %s) nhung khong tim thay Refresh_Button.png trong frame.",
                frame_rect.left,
                frame_rect.top,
                frame_rect.width,
                frame_rect.height,
            )
            return None
        LOGGER.info(
            "Detect thanh cong Refresh_Button.png | conf=%.3f | rect=(%s, %s, %s, %s)",
            refresh_match.confidence,
            refresh_match.rect.left,
            refresh_match.rect.top,
            refresh_match.rect.width,
            refresh_match.rect.height,
        )
        LOGGER.info(
            "Xac dinh MainScene | frame=(%s, %s, %s, %s)",
            frame_rect.left,
            frame_rect.top,
            frame_rect.width,
            frame_rect.height,
        )

        scroll_x = min(
            frame_rect.right - 5,
            int(frame_rect.left + frame_rect.width * self.config.scroll_anchor_ratio_x),
        )
        scroll_y = refresh_match.rect.top + refresh_match.rect.height // 2
        scroll_distance = int(frame_rect.height * self.config.scroll_ratio)

        return SceneContext(
            frame_rect=frame_rect,
            refresh_button=refresh_match,
            scroll_start=Point(scroll_x, scroll_y),
            scroll_end=Point(scroll_x, max(frame_rect.top + 10, scroll_y - scroll_distance)),
        )
