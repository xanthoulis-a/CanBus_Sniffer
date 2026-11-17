# CanBus-Sniffer-UI

# Formula Student - CAN Bus Sniffer UI

A real-time Python desktop GUI built with `tkinter` and `pyserial` for sniffing, decoding, filtering, and logging Controller Area Network (CAN) bus traffic over a serial/USB interface. Designed for Formula Student vehicle diagnostics and bench debugging.

## Features

- **Smart Serial Port Detection:** Automatically filters out irrelevant Bluetooth, audio, and mobile devices to highlight valid USB-to-Serial adapters (STM32, FTDI, CP210x, CH340, etc.).
- **Multi-Baud Rate Support:** Configurable baud rates (`115200`, `230400`, `921600`, `2000000`) to match different CAN-to-UART sniffer hardware.
- **Real-Time CAN Frame Decoding:** Automatically categorizes and decodes raw payloads by CAN ID ranges:
  - `0x100 – 0x10F`: **VCU (Vehicle Control)** — Throttle (%) and Brake (%) values.
  - `0x200 – 0x205`: **Inverter / Motor** — Temperature (°C) and Current (A).
  - `0x300 – 0x310`: **BMS (Accumulator)** — Max Cell Voltage and Pack State of Charge (SoC %).
  - `Other IDs`: **General Telemetry / Unmapped IDs** — Displays raw decimal byte payloads.
- **Live Filtering & Search:** Filter bus traffic by vehicle subsystem or search dynamically by hexadecimal CAN ID.
- **Thread-Safe High-Speed Buffering:** Uses a dedicated background reader thread and bounded queue (`maxsize=3000`) to prevent UI freezes during high-frequency CAN bus traffic.
- **Session Controls & CSV Export:** Pause/resume the live table feed without dropping incoming packets in the background, clear session logs, and export captured CAN frames to `.csv` files.

## Prerequisites

- **Python 3.8+**
- **Tkinter** (Included with standard Python installations on Windows and macOS. On Linux, you may need to install it via `sudo apt-get install python3-tk`).
- A CAN-to-Serial/USB sniffer interface streaming space-delimited ASCII CAN frames.

## Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/xanthoulis-a/CanBus-Sniffer-UI.git](https://github.com/xanthoulis-a/CanBus-Sniffer-UI.git)
   cd CanBus-Sniffer-UI

 2. **Create and activate a virtual environment:**
    ```bash
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
