from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass

from Module.assets import AssetBundle, Template
from Module.capture import ScreenCapture
from Module.config import BotConfig
from Module.geometry import MatchResult, Rect
from Module.matcher import TemplateMatcher
from Module.scene import SceneContext, SceneLocator
from Module.windows_input import WindowActivator, WindowsMouseController


LOGGER = logging.getLogger("secret_shop_bot")


@dataclass
class PurchaseStats:
    mystic_medals: int = 0
    covenant_bookmarks: int = 0
    refresh_count: int = 0


class SecretShopBot:
    def __init__(
        self,
        config: BotConfig,
        assets: AssetBundle,
        capture: ScreenCapture,
        matcher: TemplateMatcher,
        scene_locator: SceneLocator,
    ) -> None:
        self.config = config
        self.assets = assets
        self.capture = capture
        self.matcher = matcher
        self.scene_locator = scene_locator
        self.stats = PurchaseStats()
        self.mouse = WindowsMouseController()
        self.window_activator = WindowActivator(config.window_title_keyword)

    def run(self) -> None:
        LOGGER.info("Bat dau bot. Su dung Windows native mouse input de click vao game.")
        scene = self._wait_for_scene()
        LOGGER.info("Da xac dinh duoc MainScene tai %s", scene.frame_rect)

        while True:
            self._random_idle()
            self._run_single_shop_cycle(scene)

    def _run_single_shop_cycle(self, scene: SceneContext) -> None:
        bought_mm = False
        bought_cb = False

        for pass_index in range(2):
            scene = self._wait_for_scene()
            frame = self.capture.grab()
            scene_image = self.capture.crop(frame.image, scene.frame_rect)

            if not bought_mm:
                bought_mm = self._attempt_buy_item(
                    scene=scene,
                    scene_image=scene_image,
                    item_template=self.assets.mm_item,
                    confirm_template=self.assets.buy_mm_button,
                ) or bought_mm
            if not bought_cb:
                bought_cb = self._attempt_buy_item(
                    scene=scene,
                    scene_image=scene_image,
                    item_template=self.assets.cb_item,
                    confirm_template=self.assets.buy_cb_button,
                ) or bought_cb

            if bought_mm and bought_cb:
                break

            if pass_index == 0:
                self._scroll_shop(scene)

        self._refresh_shop(scene)
        self.stats.refresh_count += 1
        LOGGER.info(
            "Tong ket sau refresh #%s | MM=%s | CB=%s",
            self.stats.refresh_count,
            self.stats.mystic_medals,
            self.stats.covenant_bookmarks,
        )

    def _attempt_buy_item(
        self,
        scene: SceneContext,
        scene_image,
        item_template: Template,
        confirm_template: Template,
    ) -> bool:
        item_match = self.matcher.find_best(
            scene_image,
            item_template,
            self.config.match.item_threshold,
            offset_x=scene.frame_rect.left,
            offset_y=scene.frame_rect.top,
        )
        if item_match is None:
            return False

        LOGGER.info(
            "Detect thanh cong %s | conf=%.3f | rect=(%s, %s, %s, %s)",
            item_template.path.name,
            item_match.confidence,
            item_match.rect.left,
            item_match.rect.top,
            item_match.rect.width,
            item_match.rect.height,
        )
        buy_region = self._build_buy_region(scene.frame_rect, item_match)
        frame = self.capture.grab()
        buy_region_clamped = buy_region.clamp(frame.width, frame.height)
        buy_region_image = self.capture.crop(frame.image, buy_region_clamped)
        buy_match = self.matcher.find_best(
            buy_region_image,
            self.assets.buy_button,
            self.config.match.button_threshold,
            offset_x=buy_region_clamped.left,
            offset_y=buy_region_clamped.top,
        )
        if buy_match is None:
            LOGGER.debug("Tim thay %s nhung khong tim duoc nut Buy tuong ung.", item_template.name)
            return False

        LOGGER.info(
            "Detect thanh cong Buy_Button.png | conf=%.3f | rect=(%s, %s, %s, %s)",
            buy_match.confidence,
            buy_match.rect.left,
            buy_match.rect.top,
            buy_match.rect.width,
            buy_match.rect.height,
        )
        LOGGER.info("Da tim thay %s (conf=%.3f). Tien hanh mua.", item_template.name, item_match.confidence)
        self._click_match(buy_match)
        time.sleep(self.config.timing.post_click_delay)

        confirm_match = self._wait_for_template(confirm_template, self.config.match.confirm_threshold)
        self._click_match(confirm_match)
        time.sleep(self.config.timing.post_click_delay)
        self._wait_for_scene()

        if item_template.name == "MysticsMedals":
            self.stats.mystic_medals += 1
        else:
            self.stats.covenant_bookmarks += 1
        return True

    def _build_buy_region(self, frame_rect: Rect, item_match: MatchResult) -> Rect:
        top_padding = int(item_match.rect.height * 0.25)
        bottom_padding = int(item_match.rect.height * 0.25)
        return Rect(
            left=item_match.rect.right,
            top=max(frame_rect.top, item_match.rect.top - top_padding),
            width=max(10, frame_rect.right - item_match.rect.right),
            height=max(10, item_match.rect.height + top_padding + bottom_padding),
        )

    def _refresh_shop(self, scene: SceneContext) -> None:
        LOGGER.info("Khong con item can mua trong vong hien tai. Tien hanh refresh shop.")
        LOGGER.info(
            "Su dung Refresh_Button.png tai rect=(%s, %s, %s, %s)",
            scene.refresh_button.rect.left,
            scene.refresh_button.rect.top,
            scene.refresh_button.rect.width,
            scene.refresh_button.rect.height,
        )
        self._click_match(scene.refresh_button)
        time.sleep(self.config.timing.post_click_delay)
        confirm_match = self._wait_for_template(
            self.assets.confirm_refresh_button,
            self.config.match.confirm_threshold,
        )
        self._click_match(confirm_match)
        time.sleep(self.config.timing.after_refresh_delay)
        self._wait_for_scene()

    def _scroll_shop(self, scene: SceneContext) -> None:
        LOGGER.debug(
            "Scroll shop tu (%s, %s) den (%s, %s).",
            scene.scroll_start.x,
            scene.scroll_start.y,
            scene.scroll_end.x,
            scene.scroll_end.y,
        )
        self.window_activator.activate()
        self.mouse.drag(scene.scroll_start, scene.scroll_end, duration=0.35)
        time.sleep(self.config.timing.after_scroll_delay)

    def _wait_for_scene(self) -> SceneContext:
        deadline = time.time() + self.config.timing.scene_timeout
        attempt = 0
        while time.time() < deadline:
            attempt += 1
            frame = self.capture.grab()
            scene = self.scene_locator.locate(frame.image, frame.width, frame.height)
            if scene is not None:
                return scene
            LOGGER.debug("Lan thu #%s: chua xac dinh duoc MainScene, se thu lai.", attempt)
            time.sleep(self.config.timing.frame_interval)
        raise TimeoutError("Khong the xac dinh MainScene trong thoi gian cho phep.")

    def _wait_for_template(self, template: Template, threshold: float) -> MatchResult:
        deadline = time.time() + self.config.timing.confirm_timeout
        while time.time() < deadline:
            frame = self.capture.grab()
            match = self.matcher.find_best(frame.image, template, threshold)
            if match is not None:
                LOGGER.info(
                    "Detect thanh cong %s | conf=%.3f | rect=(%s, %s, %s, %s)",
                    template.path.name,
                    match.confidence,
                    match.rect.left,
                    match.rect.top,
                    match.rect.width,
                    match.rect.height,
                )
                return match
            time.sleep(self.config.timing.frame_interval)
        raise TimeoutError(f"Khong the tim thay template xac nhan: {template.name}")

    def _click_match(self, match: MatchResult) -> None:
        activated = self.window_activator.activate()
        LOGGER.debug(
            "Click tai tam rect=(%s, %s) | foreground=%s",
            match.rect.center.x,
            match.rect.center.y,
            activated,
        )
        self.mouse.click(
            match.rect.center.x,
            match.rect.center.y,
            press_duration=self.config.timing.click_press_duration,
        )

    def _random_idle(self) -> None:
        time.sleep(random.uniform(
            self.config.timing.action_delay_min,
            self.config.timing.action_delay_max,
        ))
