# FreeCAD MCP

## Overview

The FreeCAD MCP (Model Control Protocol) provides a simplified interface for interacting with FreeCAD through a server-client architecture. This allows users to execute commands and retrieve information about the current FreeCAD document and scene.

https://github.com/user-attachments/assets/
5acafa17-4b5b-4fef-9f6c-617e85357d44

## Features


The FreeCAD MCP currently supports the following functionalities:

### 1. `get_scene_info`

- **Description**: Retrieves comprehensive information about the current FreeCAD document, including:
  - Document properties (name, label, filename, object count)
  - Detailed object information (type, position, rotation, shape properties)
  - Sketch data (geometry, constraints)
  - View information (camera position, direction, etc.)

- **Usage**: This command can be called to get a snapshot of the current state of the FreeCAD environment, which is useful for understanding the context of the model being worked on.

### 2. `run_script`

- **Description**: Executes arbitrary Python code within the FreeCAD context. This allows users to perform complex operations, create new objects, modify existing ones, and automate tasks using FreeCAD's Python API.

- **Usage**: Users can send a Python script as a string to this command, which will be executed in the FreeCAD environment. This is particularly useful for custom automation and scripting tasks.

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

## Installation

1. Clone the repository or download the files.
2. Place the `freecad_mcp` directory in your FreeCAD modules directory:
   - Windows: `%APPDATA%/FreeCAD/Mod/`
   - Linux: `~/.FreeCAD/Mod/`
   - macOS: `~/Library/Preferences/FreeCAD/Mod/`
3. Restart FreeCAD and select the "FreeCAD MCP" workbench from the workbench selector.

## Contributing

Feel free to contribute by submitting issues or pull requests. Your feedback and contributions are welcome!

## License

This project is licensed under the MIT License. See the LICENSE file for details.
