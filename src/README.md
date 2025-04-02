<h1 align="center">FreeCAD MCP Source Code</h1>

<p align="center">
   <a href="README_JP.md"><img src="https://img.shields.io/badge/ドキュメント-日本語-white.svg" alt="JA doc"/></a>
   <a href="README.md"><img src="https://img.shields.io/badge/english-document-white.svg" alt="EN doc"></a>
</p>

## 🔧 Core Components

### `freecad_bridge.py`

Main bridge component between MCP server and FreeCAD.

#### Functions

##### `send_to_freecad(command: Dict[str, Any]) -> Dict[str, Any]`
Handles socket communication with FreeCAD:
- Creates socket connection
- Sends JSON-formatted commands
- Receives and parses responses
- Handles connection errors

##### `@mcp.tool() send_command(command: str) -> str`
Sends commands to FreeCAD and retrieves document context:
- Executes given command
- Returns document information
- Includes active objects and properties
- Provides current view state

##### `@mcp.tool() run_script(script: str) -> str`
Executes Python scripts in FreeCAD context:
- Runs arbitrary Python code
- Returns execution results as JSON
- Handles script execution errors

#### Constants

- `FREECAD_HOST`: Server host (default: 'localhost')
- `FREECAD_PORT`: Server port (default: 9876)

#### Server Configuration

Uses FastMCP server initialization:
```python
mcp = FastMCP("freecad-bridge")
mcp.run(transport='stdio')
```
