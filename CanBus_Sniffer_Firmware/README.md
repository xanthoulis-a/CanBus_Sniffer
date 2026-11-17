# CanBus-Sniffer-Board-Code

# Formula Student - CAN Bus Sniffer Firmware

Firmware implementation for the **Formula Student** CAN Bus Sniffer, built using **STM32CubeIDE** for the **STM32G4** family (`STM32G491KCUX`). This firmware listens to the vehicle's CAN bus network, processes incoming frames, and streams them over UART (USB Virtual COM Port / Serial) to the companion [CanBus-Sniffer-UI](https://github.com/xanthoulis-a/CanBus-Sniffer-UI).

## Hardware Specifications

- **Microcontroller:** STM32G491KC (ARM Cortex-M4 32-bit MCU with FPU)
- **Peripherals Used:**
  - **FDCAN / CAN Controller:** Configured to interface with the vehicle's CAN transceiver.
  - **USART / UART:** Transmits parsed CAN frames formatted as ASCII strings to the host PC.
- **Development Environment:** STM32CubeIDE (using STM32CubeMX `.ioc configuration`)

## Features

- High-speed CAN frame reception using hardware mailboxes/filters.
- Real-time packaging of incoming CAN IDs, Data Length Codes (DLC), and raw payloads.
- Space-delimited ASCII string transmission over UART matching the desktop GUI parser requirements.

## Project Structure

```text
CANBus_Sniffer/
│
├── Core/
│   ├── Inc/               # Header files (.h)
│   ├── Src/               # Source files (.main, can, usart, etc.)
│   └── Startup/           # MCU startup assembly script
├── Drivers/               # STM32G4 HAL drivers and CMSIS
├── Debug/                 # Build outputs and object files
├── CANBus_Sniffer.ioc     # STM32CubeMX configuration file
├── STM32G491KCUX_FLASH.ld # Linker script for Flash memory
└── STM32G491KCUX_RAM.ld   # Linker script for RAM

