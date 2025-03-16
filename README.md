# Chrono Info Widget

A compact widget developed in Python with Tkinter, which combines a customizable timer with real-time system usage monitoring. Ideal for timed tasks, it offers a lightweight and discreet alternative to the Windows Clock program. Designed without borders, it allows flexible positioning and saves space, making it perfect for the Windows Taskbar. A sound alert notifies when the time is up.

![Chrono Info Widget](https://github.com/LoukasLoukanos/Chrono-Info-Widget/blob/master/PREVIEW.gif)

## Features

*   **Minimalist Timer:**
    *   Simple and direct interface.
    *   Configurable countdown.
    *   Play/pause and reset buttons.
*   **System Monitoring:**
    *   CPU usage (%).
    *   RAM usage (%, GB used/total).
    *   Disk usage (MB/s read/write, GB used/total).
*   **Settings:**
    *   Window position is saved and restored.
    *   Always on top interface.
*   **Sound Notification:**
    *   Emits a sound when the time reaches zero.
*   **Drag and Drop:**
    *   Window can be dragged across the screen by clicking and dragging on the timer panel.

## How to Use

1.  **Prerequisites:**
    *   Python 3.x
    *   Libraries: `tkinter`, `psutil`

    ```
    pip install psutil
    ```

2.  **Execution:**

    ```
    python crono.pyw
    ```

    or execute the compiled executable from the .pyw file.

## Configuration

*   Window settings (position and remaining time) are stored in the `mini_timer_config.json` file.

## To Do

*   Implement visual customization options.
*   Add more system metrics (network usage, etc.).
*   Theme support.
*   Add progressive counter option
*   Implement notification and alarm system
*   Add option to run on system startup

## Developer

*   Lucas Chagas Ribeiro (2025)

## License

This project is under the MIT license. See the `LICENSE` file for more details.
