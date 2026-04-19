from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from Module.config import BotConfig


@dataclass(frozen=True)
class Template:
    name: str
    path: Path
    image: np.ndarray
    width: int
    height: int


@dataclass(frozen=True)
class AssetBundle:
    top_left: Template
    top_right: Template
    refresh_button: Template
    confirm_refresh_button: Template
    buy_button: Template
    buy_mm_button: Template
    buy_cb_button: Template
    mm_item: Template
    cb_item: Template


def _load_template(path: Path, name: str) -> Template:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Khong the doc template: {path}")
    height, width = image.shape[:2]
    return Template(name=name, path=path, image=image, width=width, height=height)


def load_assets(config: BotConfig) -> AssetBundle:
    base = config.paths.images_dir
    return AssetBundle(
        top_left=_load_template(base / "frameDetect" / "image_TopLeft.png", "top_left"),
        top_right=_load_template(base / "frameDetect" / "image_TopRight.png", "top_right"),
        refresh_button=_load_template(base / "Buttons" / "Refresh_Button.png", "refresh_button"),
        confirm_refresh_button=_load_template(
            base / "Buttons" / "ConfirmRefresh_Button.png",
            "confirm_refresh_button",
        ),
        buy_button=_load_template(base / "Buttons" / "Buy_Button.png", "buy_button"),
        buy_mm_button=_load_template(base / "Buttons" / "BuyMM_Button.png", "buy_mm_button"),
        buy_cb_button=_load_template(base / "Buttons" / "BuyCB_Button.png", "buy_cb_button"),
        mm_item=_load_template(base / "ImageIcon" / "MM_Image.png", "MysticsMedals"),
        cb_item=_load_template(base / "ImageIcon" / "CB_Image.png", "CovenantBookmarks"),
    )
