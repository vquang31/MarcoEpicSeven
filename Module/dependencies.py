from __future__ import annotations

import importlib


REQUIRED_PACKAGES = {
    "cv2": "opencv-python",
    "numpy": "numpy",
    "mss": "mss",
}


def validate_runtime_dependencies() -> list[str]:
    missing: list[str] = []
    for module_name, package_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except Exception:
            missing.append(package_name)
    return missing
