# MarcoEpicSeven

MarcoEpicSeven is a Python automation tool for the Epic Seven Secret Shop. It scans the screen, detects shop items with OpenCV template matching, buys `Mystic Medals` and `Covenant Bookmarks` when they appear, scrolls the shop, and refreshes the shop automatically.

The bot works by:

- Detecting the game window frame from `image_TopLeft.png` and `image_TopRight.png`
- Locating the `Refresh` button inside the detected scene
- Searching for target item icons in the shop area
- Clicking the correct `Buy` button and the matching confirmation button
- Scrolling once to check the lower part of the shop
- Refreshing the shop and repeating the cycle

## Requirements

- Windows
- Python 3.10 or newer recommended
- Epic Seven window visible on screen
- Screen resolution: `1980x1080`

## Required Libraries

This project requires:

- `opencv-python`
- `numpy`
- `mss`

## Install Dependencies

Install the required packages with:

```bash
pip install opencv-python numpy mss
```

If you want, you can also create a virtual environment first:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install opencv-python numpy mss
```

## How To Use

1. Open Epic Seven.
2. Move the game window to the **top-left corner** of your monitor.
3. Resize the game window so it uses about **one quarter of the screen**.
4. Make sure the game scene matches the expected Secret Shop layout.
5. Run the bot:

```bash
python main.py
```

The program will:

- Detect the game scene from the top-left and top-right anchor images
- Look for `Mystic Medals` and `Covenant Bookmarks`
- Buy them automatically
- Scroll the shop once
- Refresh and continue

Keyboard controls while the bot is running:

- Press `Q` to pause
- Press `R` to resume

## Important Note About Resolution

This program is currently tuned for a `1980x1080` screen setup.

Because the bot uses template matching, different monitor resolutions, display scaling, emulator scaling, or window sizes can reduce detection accuracy. If your setup is different, you will likely need to adjust the matching configuration and possibly replace the template images in `imagesDetect/`.

## Adjusting For Other Screen Configurations

If you use a different resolution or a different window scale, check these areas:

### 1. Update `scale_values`

File: [Module/config.py](/Module/config.py)

`scale_values` controls how many size variations the bot tests when matching template images.

Current location:

```python
class MatchConfig:
    scale_values: tuple[float, ...] = (...)
```

How to adjust:

- Increase the range if your game window is smaller or larger than the original setup
- Add more values for finer matching accuracy
- Reduce the list if matching is too slow

Example:

```python
scale_values: tuple[float, ...] = (
    0.40, 0.45, 0.50, 0.55, 0.60,
    0.65, 0.70, 0.75, 0.80, 0.85,
    0.90, 0.95, 1.00, 1.05, 1.10,
    1.15, 1.20, 1.25, 1.30, 1.35,
    1.40, 1.45, 1.50, 1.55, 1.60,
)
```

### 2. Update Threshold Values

File: [Module/config.py](/Module/config.py)

Thresholds control how confident OpenCV must be before a match is accepted:

- `scene_threshold`
- `button_threshold`
- `item_threshold`
- `confirm_threshold`

How to adjust:

- Lower a threshold if the bot often fails to detect a valid image
- Raise a threshold if the bot clicks the wrong target

Example:

```python
class MatchConfig:
    scene_threshold: float = 0.72
    button_threshold: float = 0.80
    item_threshold: float = 0.70
    confirm_threshold: float = 0.79
```

Suggested tuning rule:

- Start by changing values in small steps such as `0.02` or `0.05`
- If detection is unstable, test one threshold at a time

### 3. Update Time-Out and Delay Settings

File: [Module/config.py](/Module/config.py)

Timing is controlled in `TimingConfig`:

- `frame_interval`: how often the screen is checked
- `action_delay_min` / `action_delay_max`: random delay between shop cycles
- `post_click_delay`: wait after clicking
- `confirm_timeout`: maximum wait time for confirmation buttons
- `scene_timeout`: maximum wait time to detect the main scene
- `after_scroll_delay`: wait after dragging the shop
- `after_refresh_delay`: wait after confirming refresh
- `click_press_duration`: how long the mouse button stays pressed

Example:

```python
class TimingConfig:
    frame_interval: float = 0.20
    action_delay_min: float = 0.10
    action_delay_max: float = 0.20
    post_click_delay: float = 0.10
    confirm_timeout: float = 600.0
    scene_timeout: float = 800.0
    after_scroll_delay: float = 0.2
    after_refresh_delay: float = 0.05
    click_press_duration: float = 0.06
```

How to adjust:

- Increase delays if the game or emulator responds slowly
- Increase `confirm_timeout` or `scene_timeout` if detection takes too long
- Reduce delays if your system is stable and you want faster execution

## When You Should Replace Template Images

You may need to update the images inside `imagesDetect/` if:

- Your emulator uses a different UI scale
- Your game language changes the button appearance
- Your monitor scaling changes the captured size too much
- The bot detects the wrong buttons or items even after threshold tuning

Important folders:

- `imagesDetect/frameDetect/`
- `imagesDetect/Buttons/`
- `imagesDetect/ImageIcon/`

## Project Structure

- `main.py`: program entry point
- `Module/config.py`: all main thresholds, timing values, and scale settings
- `Module/bot.py`: main automation loop
- `Module/scene.py`: scene and refresh-button detection
- `Module/matcher.py`: OpenCV template matching across multiple scales
- `Module/capture.py`: full-screen capture
- `imagesDetect/`: template images used by the bot

## Notes

- The bot reads the full screen and sends real mouse input on Windows.
- Run the game in a stable position and do not move the window while the bot is working.
- `main.py` attempts to restart with Administrator permission on Windows if needed.
- Matching quality depends heavily on the template images and your screen setup.
