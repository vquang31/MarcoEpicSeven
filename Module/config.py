from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class MatchConfig:
    scene_threshold: float = 0.72
    button_threshold: float = 0.80
    item_threshold: float = 0.77
    confirm_threshold: float = 0.79
    scale_values: tuple[float, ...] = (
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
    )


@dataclass(frozen=True)
class TimingConfig:
    frame_interval: float = 0.20
    action_delay_min: float = 0.50
    action_delay_max: float = 1.00
    post_click_delay: float = 0.70
    confirm_timeout: float = 6.0
    scene_timeout: float = 8.0
    after_scroll_delay: float = 0.65
    after_refresh_delay: float = 1.20
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
