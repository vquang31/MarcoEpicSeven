from __future__ import annotations

import ctypes
import logging
import os
import sys
from pathlib import Path

from Module.config import build_default_config
from Module.dependencies import validate_runtime_dependencies


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def ensure_admin() -> int | None:
    if os.name != "nt":
        return None

    try:
        is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        is_admin = False

    if is_admin:
        return None

    script_path = Path(__file__).resolve()
    params = " ".join([f'"{script_path}"', *[f'"{arg}"' for arg in sys.argv[1:]]])
    result = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        params,
        str(script_path.parent),
        1,
    )
    if result <= 32:
        logging.getLogger("main").error("Khong the mo lai chuong trinh voi quyen Administrator.")
        return 1

    logging.getLogger("main").info("Dang mo lai chuong trinh voi quyen Administrator.")
    return 0


def main() -> int:
    configure_logging()
    logger = logging.getLogger("main")

    admin_result = ensure_admin()
    if admin_result is not None:
        return admin_result

    missing_packages = validate_runtime_dependencies()
    if missing_packages:
        logger.error("Moi truong dang thieu thu vien can thiet: %s", ", ".join(missing_packages))
        logger.error("Hay cai dat bang lenh: pip install %s", " ".join(missing_packages))
        return 1

    from Module.assets import load_assets
    from Module.bot import SecretShopBot
    from Module.capture import ScreenCapture
    from Module.matcher import TemplateMatcher
    from Module.scene import SceneLocator

    root_dir = Path(__file__).resolve().parent
    config = build_default_config(root_dir)
    assets = load_assets(config)
    matcher = TemplateMatcher(config.match.scale_values)
    capture = ScreenCapture()
    scene_locator = SceneLocator(assets, matcher, config)
    bot = SecretShopBot(
        config=config,
        assets=assets,
        capture=capture,
        matcher=matcher,
        scene_locator=scene_locator,
    )

    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Da nhan lenh dung chuong trinh.")
        return 0
    except Exception as exc:
        logger.exception("Chuong trinh dung do loi: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
