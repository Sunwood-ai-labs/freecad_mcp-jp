# FreeCAD MCP

A FreeCAD addon that implements the Model Context Protocol (MCP) to enable communication between FreeCAD and Claude AI through Claude Desktop.

My initial work os based on the  ([Blender MCP Repository](https://github.com/ahujasid/blender-mcp)

<video src=\"https://github.com/bonninr/freecad_mcp/assets/freecad.mp4" controls=\"controls\" style=\"max-width: 730px;\"></video>

## Overview

FreeCAD MCP is an addon that allows you to control FreeCAD using natural language through Claude AI. It implements the Model Context Protocol (MCP) to establish a bridge between Claude Desktop and FreeCAD, enabling:

- Creation and manipulation of 3D objects
- Parametric modeling operations
- Document management
- Export and import operations
- And more...

## Installation

1. Clone this repository into your FreeCAD Mod directory:
   ```bash
   cd ~/.FreeCAD/Mod  # Linux/Mac
   # or
   cd %APPDATA%/FreeCAD/Mod  # Windows
   
   git clone https://github.com/yourusername/freecad-mcp.git
   ```

2. Install the required Python packages:
   ```bash
   pip install mcp-server
   ```

3. Restart FreeCAD

## Usage

1. Start FreeCAD
2. Select the "FreeCAD MCP" workbench from the workbench selector
3. Click the "Show FreeCAD MCP Panel" button in the toolbar
4. Click "Start Server" in the panel
5. Start Claude Desktop with the appropriate configuration

### Claude Desktop Configuration

Configure Claude Desktop to use the FreeCAD MCP bridge by adding the following configuration:

```json
{
  "command": "python",
  "args": ["src/freecad_bridge.py"],
  "env": {
    "PYTHONPATH": "C:\\Program Files\\FreeCAD 1.0\\bin"
  }
}
```

## Features

The addon provides the following main features through the MCP protocol:

### Object Creation
- Create basic shapes (Box, Cylinder, Sphere, Cone, Torus)
- Create sketches with various geometric elements
- Create Draft objects (Rectangle, Circle, Polygon)

### Object Manipulation
- Modify object properties (position, rotation, dimensions)
- Apply boolean operations (union, cut, intersection)
- Create fillets and chamfers
- Create arrays (rectangular and polar)

### Sketch Operations
- Add geometric elements (lines, circles, arcs)
- Apply constraints (distance, angle, parallel, etc.)

### Document Management
- Get document and object information
- Save documents
- Export objects to various formats (STEP, IGES, STL)

## Development

### Project Structure
```
freecad-mcp/
├── Init.py              # FreeCAD addon initialization
├── InitGui.py          # FreeCAD GUI initialization
├── addon.py            # Main addon implementation
├── src/
│   └── freecad_bridge.py   # MCP bridge implementation
├── assets/             # Icons and resources
└── docs/              # Documentation
```

### Adding New Features

To add new features:

1. Implement the feature in `addon.py` using FreeCAD's Python API
2. Add corresponding MCP tool in `freecad_bridge.py`
3. Update documentation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FreeCAD development team
- Model Context Protocol (MCP) developers
- Claude AI team at Anthropic

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/freecad-mcp/issues) page
2. Create a new issue with a detailed description
3. Join the discussion in the FreeCAD forum
