from __future__ import annotations

import ctypes
import logging
import time
from ctypes import wintypes

from Module.geometry import Point


LOGGER = logging.getLogger("secret_shop_bot")

user32 = ctypes.WinDLL("user32", use_last_error=True)

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SW_RESTORE = 9
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
MK_LBUTTON = 0x0001


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]


class WindowsMouseController:
    def __init__(self) -> None:
        self.virtual_left = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
        self.virtual_top = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
        self.virtual_width = max(1, user32.GetSystemMetrics(SM_CXVIRTUALSCREEN))
        self.virtual_height = max(1, user32.GetSystemMetrics(SM_CYVIRTUALSCREEN))

    def move_to(self, x: int, y: int) -> None:
        dx, dy = self._normalize(x, y)
        self._send_mouse_input(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK, dx, dy)

    def click(self, x: int, y: int, press_duration: float = 0.05) -> None:
        self.move_to(x, y)
        time.sleep(0.02)
        dx, dy = self._normalize(x, y)
        self._send_mouse_input(
            MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_LEFTDOWN,
            dx,
            dy,
        )
        time.sleep(press_duration)
        self._send_mouse_input(
            MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_LEFTUP,
            dx,
            dy,
        )

    def drag(self, start: Point, end: Point, duration: float = 0.35) -> None:
        steps = max(3, int(duration / 0.02))
        self.move_to(start.x, start.y)
        time.sleep(0.03)
        start_dx, start_dy = self._normalize(start.x, start.y)
        self._send_mouse_input(
            MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_LEFTDOWN,
            start_dx,
            start_dy,
        )
        try:
            for step in range(1, steps + 1):
                t = step / steps
                x = round(start.x + (end.x - start.x) * t)
                y = round(start.y + (end.y - start.y) * t)
                dx, dy = self._normalize(x, y)
                self._send_mouse_input(
                    MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK,
                    dx,
                    dy,
                )
                time.sleep(duration / steps)
        finally:
            end_dx, end_dy = self._normalize(end.x, end.y)
            self._send_mouse_input(
                MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_LEFTUP,
                end_dx,
                end_dy,
            )

    def _normalize(self, x: int, y: int) -> tuple[int, int]:
        normalized_x = round((x - self.virtual_left) * 65535 / max(1, self.virtual_width - 1))
        normalized_y = round((y - self.virtual_top) * 65535 / max(1, self.virtual_height - 1))
        return normalized_x, normalized_y

    def _send_mouse_input(self, flags: int, dx: int, dy: int) -> None:
        input_struct = INPUT(
            type=INPUT_MOUSE,
            union=INPUT_UNION(
                mi=MOUSEINPUT(
                    dx=dx,
                    dy=dy,
                    mouseData=0,
                    dwFlags=flags,
                    time=0,
                    dwExtraInfo=None,
                )
            ),
        )
        sent = user32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(INPUT))
        if sent != 1:
            error_code = ctypes.get_last_error()
            raise OSError(error_code, f"Khong gui duoc chuot bang SendInput (WinError {error_code}).")


class WindowActivator:
    def __init__(self, title_keyword: str) -> None:
        self.title_keyword = title_keyword.lower()

    def activate(self) -> bool:
        hwnd = self.find_window()
        if not hwnd:
            LOGGER.debug("Khong tim thay cua so co tieu de chua: %s", self.title_keyword)
            return False
        user32.ShowWindow(hwnd, SW_RESTORE)
        if not user32.SetForegroundWindow(hwnd):
            LOGGER.debug("Khong dua duoc cua so len foreground, nhung van tiep tuc gui chuot.")
            return False
        time.sleep(0.05)
        return True

    def find_window(self) -> int | None:
        found: list[int] = []

        EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        def callback(hwnd: int, lparam: int) -> bool:
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value.lower()
            if self.title_keyword in title:
                found.append(hwnd)
                return False
            return True

        user32.EnumWindows(EnumWindowsProc(callback), 0)
        return found[0] if found else None


class WindowsMessageController:
    def __init__(self, window_activator: WindowActivator) -> None:
        self.window_activator = window_activator
        user32.ScreenToClient.argtypes = [wintypes.HWND, ctypes.POINTER(POINT)]
        user32.ScreenToClient.restype = wintypes.BOOL
        user32.PostMessageW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user32.PostMessageW.restype = wintypes.BOOL

    def click(self, x: int, y: int, press_duration: float = 0.05) -> None:
        hwnd = self._require_window()
        self._post_mouse_message(hwnd, WM_MOUSEMOVE, x, y)
        self._post_mouse_message(hwnd, WM_LBUTTONDOWN, x, y, MK_LBUTTON)
        try:
            time.sleep(press_duration)
        finally:
            self._post_mouse_message(hwnd, WM_LBUTTONUP, x, y)

    def drag(self, start: Point, end: Point, duration: float = 0.35) -> None:
        hwnd = self._require_window()
        self._post_mouse_message(hwnd, WM_MOUSEMOVE, start.x, start.y)
        self._post_mouse_message(hwnd, WM_LBUTTONDOWN, start.x, start.y, MK_LBUTTON)
        steps = max(3, int(duration / 0.02))
        try:
            for step in range(1, steps + 1):
                t = step / steps
                x = round(start.x + (end.x - start.x) * t)
                y = round(start.y + (end.y - start.y) * t)
                self._post_mouse_message(hwnd, WM_MOUSEMOVE, x, y, MK_LBUTTON)
                time.sleep(duration / steps)
        finally:
            self._post_mouse_message(hwnd, WM_LBUTTONUP, end.x, end.y)

    def _require_window(self) -> int:
        hwnd = self.window_activator.find_window()
        if not hwnd:
            raise RuntimeError(
                f"Khong tim thay cua so co tieu de chua: {self.window_activator.title_keyword}"
            )
        return hwnd

    @staticmethod
    def _post_mouse_message(
        hwnd: int,
        message: int,
        screen_x: int,
        screen_y: int,
        key_state: int = 0,
    ) -> None:
        point = POINT(screen_x, screen_y)
        if not user32.ScreenToClient(hwnd, ctypes.byref(point)):
            error_code = ctypes.get_last_error()
            raise OSError(error_code, f"Khong doi duoc toa do cua so (WinError {error_code}).")
        coordinates = ((point.y & 0xFFFF) << 16) | (point.x & 0xFFFF)
        if not user32.PostMessageW(hwnd, message, key_state, coordinates):
            error_code = ctypes.get_last_error()
            raise OSError(error_code, f"Khong gui duoc thong diep chuot (WinError {error_code}).")
