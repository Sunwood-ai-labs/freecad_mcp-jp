from typing import Any, Dict, List, Optional, Union
import socket
import json
import asyncio
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("freecad-bridge")

# Constants
FREECAD_HOST = 'localhost'
FREECAD_PORT = 9876

# Supported object types and their parameters
PART_OBJECTS = {
    "Part::Box": ["Length", "Width", "Height"],
    "Part::Cylinder": ["Radius", "Height", "Angle"],
    "Part::Sphere": ["Radius", "Angle1", "Angle2", "Angle3"],
    "Part::Cone": ["Radius1", "Radius2", "Height"],
    "Part::Torus": ["Radius1", "Radius2"],
    "Part::Prism": ["Polygon", "Height"],
    "Part::RegularPolygon": ["Polygon", "Circumradius"],
    "Part::Line": ["Length"],
    "Part::Ellipse": ["MajorRadius", "MinorRadius"],
    "Part::Circle": ["Radius"],
    "Part::Point": [],
    "Part::Plane": ["Length", "Width"],
}

SKETCH_OBJECTS = {
    "Circle": ["radius", "center"],
    "Line": ["start", "end"],
    "Arc": ["center", "radius", "startangle", "endangle"],
    "Rectangle": ["x", "y", "width", "height"],
    "Polygon": ["points"],
}

async def send_to_freecad(command: Dict[str, Any]) -> Dict[str, Any]:
    """Send a command to FreeCAD and get the response."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((FREECAD_HOST, FREECAD_PORT))
        command_json = json.dumps(command)
        sock.sendall(command_json.encode('utf-8'))
        response = sock.recv(4096)
        sock.close()
        return json.loads(response.decode('utf-8'))
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def create_part_object(type: str = "Part::Box", name: Optional[str] = None,
                           dimensions: Dict[str, float] = None,
                           position: List[float] = [0, 0, 0],
                           rotation: List[float] = [0, 0, 0]) -> str:
    """Create a new Part object in FreeCAD.
    
    Args:
        type: Object type from Part workbench
        name: Name for the object (optional)
        dimensions: Dictionary of dimensions specific to the object type
        position: Object position [x, y, z]
        rotation: Object rotation [x, y, z] in degrees
    """
    if type not in PART_OBJECTS:
        return json.dumps({"status": "error", "message": f"Unsupported object type: {type}"})
    
    command = {
        "type": "create_part_object",
        "params": {
            "type": type,
            "name": name,
            "dimensions": dimensions or {},
            "position": position,
            "rotation": rotation
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def create_sketch(name: Optional[str] = None, 
                       elements: List[Dict[str, Any]] = None,
                       plane: str = "XY") -> str:
    """Create a new sketch with geometric elements.
    
    Args:
        name: Name for the sketch (optional)
        elements: List of geometric elements to add
        plane: Sketch plane (XY, XZ, YZ)
    """
    command = {
        "type": "create_sketch",
        "params": {
            "name": name,
            "elements": elements or [],
            "plane": plane
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def extrude_sketch(sketch_name: str, length: float, 
                        direction: List[float] = [0, 0, 1],
                        solid: bool = True) -> str:
    """Extrude a sketch into a 3D object.
    
    Args:
        sketch_name: Name of the sketch to extrude
        length: Length of extrusion
        direction: Direction vector [x, y, z]
        solid: Create a solid object (True) or shell (False)
    """
    command = {
        "type": "extrude_sketch",
        "params": {
            "sketch_name": sketch_name,
            "length": length,
            "direction": direction,
            "solid": solid
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def boolean_operation(name: Optional[str] = None,
                          operation: str = "union",
                          objects: List[str] = None) -> str:
    """Perform boolean operation on objects.
    
    Args:
        name: Name for the result (optional)
        operation: Type of operation (union, cut, intersection)
        objects: List of object names to operate on
    """
    command = {
        "type": "boolean_operation",
        "params": {
            "name": name,
            "operation": operation,
            "objects": objects or []
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def fillet_edge(object_name: str, radius: float, 
                     edges: List[int] = None) -> str:
    """Create a fillet on object edges.
    
    Args:
        object_name: Name of the object
        radius: Fillet radius
        edges: List of edge indices (optional, all edges if None)
    """
    command = {
        "type": "fillet_edge",
        "params": {
            "object_name": object_name,
            "radius": radius,
            "edges": edges
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def chamfer_edge(object_name: str, distance: float,
                      edges: List[int] = None) -> str:
    """Create a chamfer on object edges.
    
    Args:
        object_name: Name of the object
        distance: Chamfer distance
        edges: List of edge indices (optional, all edges if None)
    """
    command = {
        "type": "chamfer_edge",
        "params": {
            "object_name": object_name,
            "distance": distance,
            "edges": edges
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def create_array(object_name: str, array_type: str = "rectangular",
                      x_count: int = 2, y_count: int = 2, z_count: int = 1,
                      x_spacing: float = 10, y_spacing: float = 10, z_spacing: float = 10,
                      axis: List[float] = [0, 0, 1], angle: float = 360,
                      count: int = 4) -> str:
    """Create an array of objects.
    
    Args:
        object_name: Name of the base object
        array_type: Type of array (rectangular, polar)
        x_count: Number of items in X direction (rectangular)
        y_count: Number of items in Y direction (rectangular)
        z_count: Number of items in Z direction (rectangular)
        x_spacing: Spacing in X direction (rectangular)
        y_spacing: Spacing in Y direction (rectangular)
        z_spacing: Spacing in Z direction (rectangular)
        axis: Rotation axis for polar array [x, y, z]
        angle: Total angle for polar array
        count: Number of items in polar array
    """
    command = {
        "type": "create_array",
        "params": {
            "object_name": object_name,
            "array_type": array_type,
            "x_count": x_count,
            "y_count": y_count,
            "z_count": z_count,
            "x_spacing": x_spacing,
            "y_spacing": y_spacing,
            "z_spacing": z_spacing,
            "axis": axis,
            "angle": angle,
            "count": count
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def create_draft_object(type: str = "Rectangle", name: Optional[str] = None,
                            points: List[List[float]] = None,
                            properties: Dict[str, Any] = None) -> str:
    """Create a Draft workbench object.
    
    Args:
        type: Type of draft object (Rectangle, Circle, Polygon, etc.)
        name: Name for the object (optional)
        points: List of points defining the object
        properties: Additional properties for the object
    """
    command = {
        "type": "create_draft_object",
        "params": {
            "type": type,
            "name": name,
            "points": points or [],
            "properties": properties or {}
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def modify_object(name: str, 
                       position: Optional[List[float]] = None,
                       rotation: Optional[List[float]] = None,
                       scale: Optional[List[float]] = None,
                       properties: Optional[Dict[str, Any]] = None) -> str:
    """Modify an existing object's properties.
    
    Args:
        name: Name of the object to modify
        position: New position [x, y, z]
        rotation: New rotation [x, y, z] in degrees
        scale: Scale factors [x, y, z]
        properties: Object-specific properties to modify
    """
    command = {
        "type": "modify_object",
        "params": {
            "name": name
        }
    }
    if position is not None:
        command["params"]["position"] = position
    if rotation is not None:
        command["params"]["rotation"] = rotation
    if scale is not None:
        command["params"]["scale"] = scale
    if properties is not None:
        command["params"]["properties"] = properties
    
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_document_info() -> str:
    """Get information about the current FreeCAD document."""
    command = {
        "type": "get_document_info"
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_object_info(name: str) -> str:
    """Get detailed information about an object.
    
    Args:
        name: Name of the object
    """
    command = {
        "type": "get_object_info",
        "params": {
            "name": name
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def delete_object(name: str) -> str:
    """Delete an object from the document.
    
    Args:
        name: Name of the object to delete
    """
    command = {
        "type": "delete_object",
        "params": {
            "name": name
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def create_constraint(sketch_name: str, constraint_type: str,
                          elements: List[Dict[str, Any]], 
                          value: Optional[float] = None) -> str:
    """Add a constraint to a sketch.
    
    Args:
        sketch_name: Name of the sketch
        constraint_type: Type of constraint (distance, angle, etc.)
        elements: List of elements to constrain
        value: Constraint value (if applicable)
    """
    command = {
        "type": "create_constraint",
        "params": {
            "sketch_name": sketch_name,
            "constraint_type": constraint_type,
            "elements": elements,
            "value": value
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def save_document(filename: Optional[str] = None) -> str:
    """Save the current document.
    
    Args:
        filename: Path to save the file (optional)
    """
    command = {
        "type": "save_document",
        "params": {
            "filename": filename
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def export_object(name: str, filename: str, 
                       format: str = "STEP") -> str:
    """Export an object to a file.
    
    Args:
        name: Name of the object to export
        filename: Path to save the file
        format: Export format (STEP, IGES, STL, etc.)
    """
    command = {
        "type": "export_object",
        "params": {
            "name": name,
            "filename": filename,
            "format": format
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def execute_macro(macro: str) -> str:
    """Execute a FreeCAD macro.
    
    Args:
        macro: Python code to execute
    """
    command = {
        "type": "execute_macro",
        "params": {
            "macro": macro
        }
    }
    result = await send_to_freecad(command)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 