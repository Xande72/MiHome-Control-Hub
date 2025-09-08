# 🏠 MiHome Visual Control Hub

English | [中文](README.md)

A powerful **visual** MiHome device control system that integrates real-time gesture recognition, graphical device management, and intelligent control functions. Through an intuitive GUI interface and advanced computer vision technology, you can easily manage all your MiHome smart devices.

## ✨ Core Highlights

- 🎥 **Real-time Gesture Recognition Interface** - High-precision gesture detection based on MediaPipe with live camera preview
- 📊 **Visual Device Monitoring** - Graphical display of all device status, brightness, color temperature and other information
- 🖥️ **Modern GUI Interface** - Beautiful user interface based on Tkinter with multi-tab management support
- 🔍 **Smart Device Discovery** - Visual device selection and configuration export functionality
- 📈 **Real-time Status Charts** - Data visualization for device online status, response time and more

## Features

### 🔍 Visual Device Discovery & Configuration
- **Graphical Device Discovery Interface**: Automatically discover devices through Xiaomi Cloud service, displaying all MiHome devices in table format
- **Interactive Device Selection**: Provides checkbox interface for visual selection of devices to control
- **Real-time Configuration Preview**: Real-time display of device information during configuration (name, IP, token, model, etc.)
- **One-click Configuration Export**: Automatically export device information to YAML configuration file with visual editing support
- **Multi-server Region Selection**: Dropdown menu to select Xiaomi global server regions (China, Germany, USA, etc.)
- **Login Status Visualization**: Display login progress, 2FA verification status and other real-time feedback

### 👋 Real-time Gesture Recognition Control
- **Live Camera Preview Window**: Display camera feed with real-time annotation of hand keypoints and gesture recognition results
- **Visual Gesture Status**: Interface displays current recognized gesture type and confidence level in real-time
- **Multi-gesture Visual Support**:
  - 🖐️ Open Palm: Turn on all devices (green highlight)
  - ✊ Fist: Turn off all devices (red highlight)
  - 👍 Thumbs Up: Increase brightness (blue up arrow)
  - 👎 Thumbs Down: Decrease brightness (orange down arrow)
- **Gesture Recognition Visual Feedback**:
  - Real-time display of hand skeleton and keypoints
  - Visual feedback effects when gesture recognition succeeds
  - Progress bar showing gesture cooldown time
- **Smart Anti-mistouch Mechanism**: Visual display of gesture cooldown status to prevent accidental operations

### 🎛️ Visual Device Management Center
- **Device Status Dashboard**: Tree structure displaying all devices with real-time online status updates (green/red indicators)
- **Graphical Device Control Panel**:
  - Slider controls for device brightness and color temperature
  - Switch buttons for visual device status
  - Device information cards showing detailed parameters
- **Real-time Status Monitoring Interface**:
  - Device response time charts
  - Online status history records
  - Device performance metrics visualization
- **Batch Operation Console**: Checkbox selection of multiple devices for batch operations
- **Visual Device Group Management**: Display by room or type grouping with drag-and-drop support
- **Status Cache Optimization Display**: Show cache hit rate and network request statistics
- **Connection Status Visualization**: Real-time display of device connection status, timeout warnings and reconnection progress
- **One-click Refresh Function**: Button-triggered device status check with refresh progress display

## 🖼️ Interface Showcase

### Main Control Interface
- **Multi-tab Design**: Four major functional modules - Device Control, Gesture Recognition, Status Monitoring, System Settings
- **Real-time Log Display**: Bottom log panel showing system running status and operation records
- **Status Bar Information**: Display current connected device count, gesture recognition status and other key information

### Gesture Recognition Interface
- **Camera Preview Window**: 640x480 resolution real-time video stream
- **Gesture Recognition Overlay**: Hand keypoints and gesture type annotations overlaid on video
- **Recognition Status Indicators**: Color-coded display of different gesture states
- **Gesture History Log**: Display recently executed gesture commands and timestamps

### Device Management Interface
- **Device Tree View**: Hierarchical display of rooms and devices with expand/collapse support
- **Device Details Panel**: Show detailed information and control options when device is selected
- **Batch Operation Toolbar**: Button groups for quick execution of common operations
- **Device Status Charts**: Visualize device response time and online rate statistics

### Configuration Management Interface
- **Device Discovery Wizard**: Step-by-step guidance for device configuration
- **Configuration File Editor**: Syntax-highlighted YAML configuration file editing
- **Import/Export Functions**: Support configuration file backup and restore

## System Architecture

```
MiHome Integrated Control System
├── Device Discovery Module (xiaomi_device_extractor.py)
│   ├── Xiaomi Account Login
│   ├── 2FA Two-factor Authentication
│   ├── Device List Retrieval
│   └── Token Extraction
├── Gesture Control Module (mediapipe_gesture_detector.py)
│   ├── Camera Management
│   ├── Gesture Recognition
│   └── Action Mapping
├── Device Control Module (device_controller.py)
│   ├── Device Connection Management
│   ├── Status Monitoring
│   └── Control Command Sending
├── User Interface Module
│   ├── Main Control Interface (integrated_app.py)
│   ├── Device Selection Interface (device_selector_gui.py)
│   └── Device Management Interface (ui_manager.py)
└── Configuration Management Module (config_manager.py)
    ├── Device Configuration
    ├── Camera Configuration
    └── Gesture Mapping Configuration
```

## 📁 Project Structure

```
MiHome-Control-Hub/
├── main_app.py                    # Main application entry point
├── device_controller.py           # Device control core module
├── gesture_recognition.py         # Gesture recognition system
├── config_manager.py              # Configuration manager
├── token_extractor.py             # Xiaomi Cloud service authentication module
├── xiaomi_device_extractor_gui.py # Device discovery GUI tool
├── integrated_app_with_token_extractor.py # Integrated application
├── setup.py                       # Automated installation script
├── requirements.txt               # Python dependencies list
├── config.yaml                    # Configuration file (generated after running)
├── README.md                      # Project documentation (Chinese)
├── README_EN.md                   # Project documentation (English)
├── CHANGELOG.md                   # Version update log
├── CONTRIBUTING.md                # Contribution guidelines
├── LICENSE                        # Open source license
└── .gitignore                     # Git ignore file configuration
```

### Core File Descriptions
- **setup.py**: One-click installation script that automatically checks environment, installs dependencies, and creates configuration templates
- **CHANGELOG.md**: Detailed record of feature updates, performance optimizations, and bug fixes for each version
- **CONTRIBUTING.md**: Developer contribution guidelines including code standards and submission processes
- **token_extractor.py**: Xiaomi Cloud service authentication tool from the open source community

## 📋 Installation & Usage

### Quick Start (Recommended)
```bash
# Use automated installation script
python setup.py
```

### Manual Installation
#### Requirements
- Python 3.8+
- Camera device (for gesture recognition)
- Network connection (for device discovery and control)

### Installation Steps

1. **Clone Project**
   ```bash
   git clone <repository-url>
   cd MiHome-Control-Hub
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Program**
   ```bash
   python main_app.py
   ```
   
   Or use the integrated version:
   ```bash
   python integrated_app_with_token_extractor.py
   ```

### Usage Workflow

1. **First Use - Device Configuration**
   - Click "Discover and Configure MiHome Devices" button
   - Enter Xiaomi account information to login
   - Complete 2FA verification (if required)
   - Select devices to control from the device list
   - Click "Export Configuration" to save device information

2. **Start Gesture Control**
   - Ensure devices are configured
   - Click "Start Gesture Control" button
   - Camera window will display live feed
   - Make corresponding gestures in front of camera for control

3. **Device Management**
   - Click "Device Management Interface" to view all device status
   - Manually control individual devices
   - View detailed device information and status

## Supported Device Types

- **MiHome Desk Lamp Series**
  - MiHome Desk Lamp
  - MiHome Desk Lamp Pro
  - MiHome Rechargeable Desk Lamp

- **Yeelight Series**
  - Yeelight Smart Bulb
  - Yeelight Ceiling Light
  - Yeelight Color Light Strip

- **Other Lighting Devices**
  - MiHome Ceiling Light
  - MiHome Bedside Lamp
  - Third-party devices supporting miio protocol

## Gesture Guide

| Gesture | Function | Description |
|---------|----------|-------------|
| 🖐️ Open Palm | Turn On Devices | Turn on all configured devices |
| ✊ Fist | Turn Off Devices | Turn off all configured devices |
| 👍 Thumbs Up | Increase Brightness | All devices brightness +20% |
| 👎 Thumbs Down | Decrease Brightness | All devices brightness -20% |

## Configuration File Description

### config.yaml
Main configuration file containing device information and system settings:

```yaml
devices:
  Living Room Lamp:
    type: light
    ip: 192.168.1.100
    token: "your_device_token"
  Bedroom Ceiling Light:
    type: ceiling_light
    ip: 192.168.1.101
    token: "your_device_token"

camera:
  device_id: 0
  width: 640
  height: 480
  fps: 30

gesture:
  cooldown: 2.0
  confidence_threshold: 0.7
```

## Troubleshooting

### Common Issues

1. **Device Discovery Failed**
   - Check network connection
   - Confirm Xiaomi account information is correct
   - Try switching server regions

2. **Inaccurate Gesture Recognition**
   - Ensure sufficient lighting
   - Adjust camera angle
   - Keep gestures clear and stable

3. **Device Control Failed**
   - Check if device is online
   - Confirm device IP address is correct
   - Verify token validity

### Log Viewing
The program displays detailed logs in console and interface during runtime to help diagnose issues.

## 🔧 Technical Features

### Visual Technology Stack
- **Computer Vision**: Real-time gesture recognition based on Google MediaPipe with multi-hand detection support
- **GUI Framework**: Modern interface built with Tkinter supporting theme switching and responsive layout
- **Real-time Rendering**: OpenCV + PIL image processing with smooth 60FPS camera display
- **Data Visualization**: Real-time charts showing device status, performance metrics, and historical data

### System Architecture Features
- **Secure Communication**: RC4 encryption for secure communication with Xiaomi Cloud services
- **High Availability**: Comprehensive error handling, automatic reconnection, and fault recovery mechanisms
- **Performance Optimization**:
  - Smart status caching to reduce network requests
  - Multi-threading to prevent UI blocking
  - Asynchronous device control for improved responsiveness
- **Modular Design**: Loosely coupled architecture, easy to extend new device types and gestures
- **User Experience**:
  - Intuitive visual interface with real-time status feedback
  - Smart prompts and error handling
  - Support for keyboard shortcuts and right-click menus
- **Resource Management**: Background thread pool for time-consuming operations, maintaining UI responsiveness

## Development Notes

### Project Structure
```
├── main_app.py               # Main program entry (recommended)
├── integrated_app_with_token_extractor.py # Integrated application
├── xiaomi_device_extractor_gui.py # Device discovery and token extraction
├── gesture_recognition.py    # Gesture recognition
├── device_controller.py      # Device control
├── config_manager.py        # Configuration management
├── config.yaml             # Main configuration file
├── requirements.txt        # Dependencies list
└── README_EN.md           # Project documentation (English)
```

### Adding New Device Types
1. Add device type support in `device_controller.py`
2. Update configuration file template
3. Test device control functionality

### Adding New Gestures
1. Define new gestures in `gesture_recognition.py`
2. Add gesture handling logic in main application
3. Update gesture documentation

## 📄 License & Acknowledgments

This project is open source under the MIT License.

### Third-party Component Acknowledgments
- **Token Extraction Function**: token_extractor.py sourced from PiotrMachowski's open source project for Xiaomi Cloud service device token extraction
- **MediaPipe**: Google's open source machine learning framework for real-time gesture recognition
- **OpenCV**: Open source computer vision library for image processing and camera control

## 🤝 Contributing

Welcome to submit Issues and Pull Requests to improve the project!

### Contribution Guidelines
- Please include detailed reproduction steps and system information when submitting bug reports
- Please create an Issue for discussion before suggesting new features
- Code contributions should follow the project's code style and commenting standards

---

**⚠️ Important Notes**:
- Using this system requires MiHome devices to support LAN control functionality
- Some devices may need to enable developer mode or LAN control options
- First-time use is recommended under good lighting conditions for gesture recognition testing
- High-quality camera is recommended for optimal gesture recognition performance