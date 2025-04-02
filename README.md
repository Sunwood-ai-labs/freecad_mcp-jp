<p align="center">
  <img src="assets/header.png" width="100%" />
</p>

<h1 align="center">FreeCAD MCP (Model Control Protocol)</h1>

<p align="center">
  <a href="https://www.python.org"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://www.freecad.org"><img src="https://img.shields.io/badge/FreeCAD-000000?style=for-the-badge&logo=freecad&logoColor=white" alt="FreeCAD"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

<p align="center">
   <a href="README_JP.md"><img src="https://img.shields.io/badge/ドキュメント-日本語-white.svg" alt="JA doc"/></a>
   <a href="README.md"><img src="https://img.shields.io/badge/english-document-white.svg" alt="EN doc"></a>
</p>

## 🌟 Overview

The FreeCAD MCP (Model Control Protocol) provides a simplified interface for interacting with FreeCAD through a server-client architecture. This allows users to execute commands and retrieve information about the current FreeCAD document and scene.

https://github.com/user-attachments/assets/5acafa17-4b5b-4fef-9f6c-617e85357d44

## ⚙️ Configuration

To configure the MCP server, you can use a JSON format to specify the server settings. Below is an example configuration:

```json
{
    "mcpServers": {
        "freecad": {
            "command": "C:\\ProgramData\\anaconda3\\python.exe",
            "args": [
                "C:\\Users\\USER\\AppData\\Roaming\\FreeCAD\\Mod\\freecad_mcp\\src\\freecad_bridge.py"
            ]
        }
    }
}
```

### Configuration Details

- **command**: The path to the Python executable that will run the FreeCAD MCP server. This can vary based on your operating system:
  - **Windows**: Typically, it might look like `C:\\ProgramData\\anaconda3\\python.exe` or `C:\\Python39\\python.exe`.
  - **Linux**: It could be `/usr/bin/python3` or the path to your Python installation.
  - **macOS**: Usually, it would be `/usr/local/bin/python3` or the path to your Python installation.

- **args**: An array of arguments to pass to the Python command. The first argument should be the path to the `freecad_bridge.py` script, which is responsible for handling the MCP server logic. Make sure to adjust the path according to your installation.

### Example for Different Operating Systems

#### Windows
```json
{
    "mcpServers": {
        "freecad": {
            "command": "C:\\ProgramData\\anaconda3\\python.exe",
            "args": [
                "C:\\Users\\USER\\AppData\\Roaming\\FreeCAD\\Mod\\freecad_mcp\\src\\freecad_bridge.py"
            ]
        }
    }
}
```

#### Linux
```json
{
    "mcpServers": {
        "freecad": {
            "command": "/usr/bin/python3",
            "args": [
                "/home/USER/.FreeCAD/Mod/freecad_mcp/src/freecad_bridge.py"
            ]
        }
    }
}
```

#### macOS
```json
{
    "mcpServers": {
        "freecad": {
            "command": "/usr/local/bin/python3",
            "args": [
                "/Users/USER/Library/Preferences/FreeCAD/Mod/freecad_mcp/src/freecad_bridge.py"
            ]
        }
    }
}
```

## 🚀 Features

The FreeCAD MCP currently supports the following functionalities:

### 1. `get_scene_info`

- **Description**: Retrieves comprehensive information about the current FreeCAD document, including:
  - Document properties (name, label, filename, object count)
  - Detailed object information (type, position, rotation, shape properties)
  - Sketch data (geometry, constraints)
  - View information (camera position, direction, etc.)

### 2. `run_script`

- **Description**: Executes arbitrary Python code within the FreeCAD context. This allows users to perform complex operations, create new objects, modify existing ones, and automate tasks using FreeCAD's Python API.

### Example Usage

To use the FreeCAD MCP, you can connect to the server and send commands as follows:

```python
import socket
import json

# Connect to the FreeCAD MCP server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 9876))

# Example: Get scene information
command = {
    "type": "get_scene_info"
}
client.sendall(json.dumps(command).encode('utf-8'))

# Receive the response
response = client.recv(4096)
print(json.loads(response.decode('utf-8')))

# Example: Run a script
script = """
import FreeCAD
doc = FreeCAD.ActiveDocument
box = doc.addObject("Part::Box", "MyBox")
box.Length = 20
box.Width = 20
box.Height = 20
doc.recompute()
"""
command = {
    "type": "run_script",
    "params": {
        "script": script
    }
}
client.sendall(json.dumps(command).encode('utf-8'))

# Receive the response
response = client.recv(4096)
print(json.loads(response.decode('utf-8')))

# Close the connection
client.close()
```

## 🔧 Installation

1. Clone the repository or download the files.
2. Install the required Python package:
   ```bash
   pip install mcp
   ```
3. Place the `freecad_mcp` directory in your FreeCAD modules directory:
   - Windows: `%APPDATA%/FreeCAD/Mod/`
   - Linux: `~/.FreeCAD/Mod/`
   - macOS: `~/Library/Preferences/FreeCAD/Mod/`
4. Find your Python executable path:
   - Windows: Open Command Prompt and type `where python`
   - Linux/macOS: Open Terminal and type `which python3`
   Use this path in your configuration file for the `command` setting.
5. Restart FreeCAD and select the "FreeCAD MCP" workbench from the workbench selector.

## 👥 Contributing

Feel free to contribute by submitting issues or pull requests. Your feedback and contributions are welcome!

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.
