from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class MatchConfig:
    scene_threshold: float = 0.72
    button_threshold: float = 0.80
    item_threshold: float = 0.7
    confirm_threshold: float = 0.79
    scale_values: tuple[float, ...] = (
        0.55,
        0.6,
        0.65,
        0.7,
        0.75,
        0.80,
        0.85,
        0.90,
        0.95,
        1.0,
        1.05,
        1.10,
        1.15,
        1.20,
        1.25,
        1.30,
        1.35,
        1.40,
        1.45,
        1.50,
        1.55,
        1.60,
        1.65,
        1.70,
        1.75,
        1.80,
        1.85,
        1.90,
        1.95,
        2.0,
    )


@dataclass(frozen=True)
class TimingConfig:
    # frame_interval: float = 0.20
    # action_delay_min: float = 0.50
    # action_delay_max: float = 1.00
    # post_click_delay: float = 0.50
    # confirm_timeout: float = 6.0
    # scene_timeout: float = 8.0
    # after_scroll_delay: float = 0.5
    # after_refresh_delay: float = 1.0
    # click_press_duration: float = 0.06
    frame_interval: float = 0.20
    action_delay_min: float = 0.10
    action_delay_max: float = 0.20
    post_click_delay: float = 0.10
    confirm_timeout: float = 600.0
    scene_timeout: float = 800.0
    after_scroll_delay: float = 0.2
    after_refresh_delay: float = 0.05
    click_press_duration: float = 0.06

@dataclass(frozen=True)
class PathConfig:
    root_dir: Path
    images_dir: Path = field(init=False)
    module_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "images_dir", self.root_dir / "imagesDetect")
        object.__setattr__(self, "module_dir", self.root_dir / "Module")


@dataclass(frozen=True)
class BotConfig:
    paths: PathConfig
    match: MatchConfig = field(default_factory=MatchConfig)
    timing: TimingConfig = field(default_factory=TimingConfig)
    fps: int = 5
    scroll_ratio: float = 0.50
    scroll_anchor_ratio_x: float = 0.88
    scene_aspect_width: int = 16
    scene_aspect_height: int = 9
    app_always_top_left: bool = True
    window_title_keyword: str = "Epic Seven"
    debug: bool = False


def build_default_config(root_dir: str | Path) -> BotConfig:
    return BotConfig(paths=PathConfig(Path(root_dir).resolve()))
