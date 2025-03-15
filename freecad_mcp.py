import os
import FreeCAD as App
import FreeCADGui as Gui
import json
import socket
import threading
import time
import traceback
from PySide import QtCore, QtGui
import math

class FreeCADMCPServer:
    def __init__(self, host='localhost', port=9876):
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        self.client = None
        self.buffer = b''
        self.timer = None
    
    def start(self):
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            self.socket.setblocking(False)
            # Create a timer for processing server events
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self._process_server)
            self.timer.start(100)  # 100ms interval
            App.Console.PrintMessage(f"FreeCAD MCP server started on {self.host}:{self.port}\n")
        except Exception as e:
            App.Console.PrintError(f"Failed to start server: {str(e)}\n")
            self.stop()
            
    def stop(self):
        self.running = False
        if self.timer:
            self.timer.stop()
            self.timer = None
        if self.socket:
            self.socket.close()
        if self.client:
            self.client.close()
        self.socket = None
        self.client = None
        App.Console.PrintMessage("FreeCAD MCP server stopped\n")

    def _process_server(self):
        """Timer callback to process server operations"""
        if not self.running:
            return
            
        try:
            # Accept new connections
            if not self.client and self.socket:
                try:
                    self.client, address = self.socket.accept()
                    self.client.setblocking(False)
                    App.Console.PrintMessage(f"Connected to client: {address}\n")
                except BlockingIOError:
                    pass
                except Exception as e:
                    App.Console.PrintError(f"Error accepting connection: {str(e)}\n")
                
            # Process existing connection
            if self.client:
                try:
                    try:
                        data = self.client.recv(8192)
                        if data:
                            self.buffer += data
                            try:
                                command = json.loads(self.buffer.decode('utf-8'))
                                self.buffer = b''
                                response = self.execute_command(command)
                                response_json = json.dumps(response)
                                self.client.sendall(response_json.encode('utf-8'))
                            except json.JSONDecodeError:
                                pass
                        else:
                            App.Console.PrintMessage("Client disconnected\n")
                            self.client.close()
                            self.client = None
                            self.buffer = b''
                    except BlockingIOError:
                        pass
                    except Exception as e:
                        App.Console.PrintError(f"Error receiving data: {str(e)}\n")
                        self.client.close()
                        self.client = None
                        self.buffer = b''
                        
                except Exception as e:
                    App.Console.PrintError(f"Error with client: {str(e)}\n")
                    if self.client:
                        self.client.close()
                        self.client = None
                    self.buffer = b''
                    
        except Exception as e:
            App.Console.PrintError(f"Server error: {str(e)}\n")

    def execute_command(self, command):
        """Execute a command in the main FreeCAD thread"""
        try:
            cmd_type = command.get("type")
            params = command.get("params", {})
            
            handlers = {
                "get_document_info": self.get_document_info,
                "create_object": self.create_object,
                "modify_object": self.modify_object,
                "delete_object": self.delete_object,
                "get_object_info": self.get_object_info,
                "execute_code": self.execute_code,
                "create_sketch": self.create_sketch,
                "extrude_sketch": self.extrude_sketch,
                "boolean_operation": self.boolean_operation,
                "fillet_edge": self.fillet_edge,
                "chamfer_edge": self.chamfer_edge,
                "create_array": self.create_array,
                "create_draft_object": self.create_draft_object,
                "create_constraint": self.create_constraint,
                "save_document": self.save_document,
                "export_object": self.export_object,
            }
            
            handler = handlers.get(cmd_type)
            if handler:
                try:
                    App.Console.PrintMessage(f"Executing handler for {cmd_type}\n")
                    result = handler(**params)
                    return {"status": "success", "result": result}
                except Exception as e:
                    App.Console.PrintError(f"Error in handler: {str(e)}\n")
                    traceback.print_exc()
                    return {"status": "error", "message": str(e)}
            else:
                return {"status": "error", "message": f"Unknown command type: {cmd_type}"}
                
        except Exception as e:
            App.Console.PrintError(f"Error executing command: {str(e)}\n")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def get_document_info(self):
        """Get information about the current FreeCAD document"""
        try:
            doc = App.ActiveDocument
            if not doc:
                return {
                    "name": None,
                    "object_count": 0,
                    "objects": []
                }
                
            doc_info = {
                "name": doc.Name,
                "object_count": len(doc.Objects),
                "objects": []
            }
            
            for obj in doc.Objects[:10]:  # Limit to first 10 objects
                obj_info = {
                    "name": obj.Name,
                    "type": obj.TypeId,
                    "label": obj.Label,
                    "position": [
                        round(float(obj.Placement.Base.x), 2),
                        round(float(obj.Placement.Base.y), 2),
                        round(float(obj.Placement.Base.z), 2)
                    ] if hasattr(obj, "Placement") else [0, 0, 0]
                }
                doc_info["objects"].append(obj_info)
                
            return doc_info
        except Exception as e:
            App.Console.PrintError(f"Error in get_document_info: {str(e)}\n")
            traceback.print_exc()
            return {"error": str(e)}

    def create_object(self, type="Part::Box", name=None, position=(0, 0, 0), rotation=(0, 0, 0), dimensions=(10, 10, 10)):
        """Create a new object in the document"""
        doc = App.ActiveDocument
        if not doc:
            doc = App.newDocument()
            
        try:
            if type == "Part::Box":
                obj = doc.addObject("Part::Box", name or "Box")
                obj.Length = dimensions[0]
                obj.Width = dimensions[1]
                obj.Height = dimensions[2]
            elif type == "Part::Sphere":
                obj = doc.addObject("Part::Sphere", name or "Sphere")
                obj.Radius = dimensions[0] / 2
            elif type == "Part::Cylinder":
                obj = doc.addObject("Part::Cylinder", name or "Cylinder")
                obj.Radius = dimensions[0] / 2
                obj.Height = dimensions[2]
            elif type == "Part::Cone":
                obj = doc.addObject("Part::Cone", name or "Cone")
                obj.Radius1 = dimensions[0] / 2
                obj.Radius2 = 0
                obj.Height = dimensions[2]
            else:
                return {"error": f"Unsupported object type: {type}"}
                
            obj.Placement.Base = App.Vector(*position)
            obj.Placement.Rotation = App.Rotation(*rotation)
            
            doc.recompute()
            return {
                "name": obj.Name,
                "type": obj.TypeId,
                "position": list(position),
                "rotation": list(rotation)
            }
        except Exception as e:
            return {"error": str(e)}

    def modify_object(self, name, position=None, rotation=None, dimensions=None):
        """Modify an existing object"""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}
            
        try:
            obj = doc.getObject(name)
            if not obj:
                return {"error": f"Object not found: {name}"}
                
            if position is not None:
                obj.Placement.Base = App.Vector(*position)
                
            if rotation is not None:
                obj.Placement.Rotation = App.Rotation(*rotation)
                
            if dimensions is not None:
                if obj.TypeId == "Part::Box":
                    obj.Length = dimensions[0]
                    obj.Width = dimensions[1]
                    obj.Height = dimensions[2]
                elif obj.TypeId == "Part::Sphere":
                    obj.Radius = dimensions[0] / 2
                elif obj.TypeId == "Part::Cylinder":
                    obj.Radius = dimensions[0] / 2
                    obj.Height = dimensions[2]
                elif obj.TypeId == "Part::Cone":
                    obj.Radius1 = dimensions[0] / 2
                    obj.Height = dimensions[2]
                    
            doc.recompute()
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

    def delete_object(self, name):
        """Delete an object from the document"""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}
            
        try:
            obj = doc.getObject(name)
            if not obj:
                return {"error": f"Object not found: {name}"}
                
            doc.removeObject(name)
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

    def get_object_info(self, name):
        """Get detailed information about an object"""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}
            
        try:
            obj = doc.getObject(name)
            if not obj:
                return {"error": f"Object not found: {name}"}
                
            info = {
                "name": obj.Name,
                "label": obj.Label,
                "type": obj.TypeId,
                "position": [
                    round(float(obj.Placement.Base.x), 2),
                    round(float(obj.Placement.Base.y), 2),
                    round(float(obj.Placement.Base.z), 2)
                ] if hasattr(obj, "Placement") else [0, 0, 0],
                "rotation": [
                    round(float(angle), 2) for angle in obj.Placement.Rotation.toEuler()
                ] if hasattr(obj, "Placement") else [0, 0, 0],
            }
            
            # Add type-specific properties
            if obj.TypeId == "Part::Box":
                info.update({
                    "length": obj.Length,
                    "width": obj.Width,
                    "height": obj.Height
                })
            elif obj.TypeId == "Part::Sphere":
                info.update({
                    "radius": obj.Radius
                })
            elif obj.TypeId == "Part::Cylinder":
                info.update({
                    "radius": obj.Radius,
                    "height": obj.Height
                })
            elif obj.TypeId == "Part::Cone":
                info.update({
                    "radius1": obj.Radius1,
                    "radius2": obj.Radius2,
                    "height": obj.Height
                })
                
            return info
        except Exception as e:
            return {"error": str(e)}

    def execute_code(self, code):
        """Execute arbitrary Python code in FreeCAD context"""
        try:
            # Create a new dictionary with FreeCAD modules
            context = {
                'App': App,
                'Gui': Gui,
                'doc': App.ActiveDocument
            }
            
            # Execute the code
            exec(code, context)
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

    def create_sketch(self, name=None, elements=None, plane="XY"):
        """Create a new sketch with geometric elements"""
        doc = App.ActiveDocument
        if not doc:
            doc = App.newDocument()

        try:
            # Create the sketch
            sketch = doc.addObject('Sketcher::SketchObject', name or 'Sketch')
            
            # Set the sketch plane
            if plane == "XY":
                sketch.Placement = App.Placement(App.Vector(0,0,0), App.Rotation(0,0,0))
            elif plane == "XZ":
                sketch.Placement = App.Placement(App.Vector(0,0,0), App.Rotation(90,0,0))
            elif plane == "YZ":
                sketch.Placement = App.Placement(App.Vector(0,0,0), App.Rotation(0,90,0))
            
            # Add geometric elements
            if elements:
                for elem in elements:
                    elem_type = elem.get("type")
                    if elem_type == "Line":
                        start = elem.get("start", [0,0])
                        end = elem.get("end", [10,0])
                        sketch.addGeometry(Part.LineSegment(App.Vector(*start,0), App.Vector(*end,0)))
                    elif elem_type == "Circle":
                        center = elem.get("center", [0,0])
                        radius = elem.get("radius", 5)
                        sketch.addGeometry(Part.Circle(App.Vector(*center,0), App.Vector(0,0,1), radius))
                    elif elem_type == "Arc":
                        center = elem.get("center", [0,0])
                        radius = elem.get("radius", 5)
                        start_angle = elem.get("startangle", 0)
                        end_angle = elem.get("endangle", 90)
                        sketch.addGeometry(Part.ArcOfCircle(
                            Part.Circle(App.Vector(*center,0), App.Vector(0,0,1), radius),
                            math.radians(start_angle), math.radians(end_angle)
                        ))
                    elif elem_type == "Rectangle":
                        x = elem.get("x", 0)
                        y = elem.get("y", 0)
                        width = elem.get("width", 10)
                        height = elem.get("height", 10)
                        points = [
                            [x, y],
                            [x + width, y],
                            [x + width, y + height],
                            [x, y + height]
                        ]
                        for i in range(4):
                            sketch.addGeometry(Part.LineSegment(
                                App.Vector(*points[i],0), 
                                App.Vector(*points[(i+1)%4],0)
                            ))

            doc.recompute()
            return {"name": sketch.Name}
        except Exception as e:
            return {"error": str(e)}

    def extrude_sketch(self, sketch_name, length, direction=[0,0,1], solid=True):
        """Extrude a sketch into a 3D object"""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}

        try:
            sketch = doc.getObject(sketch_name)
            if not sketch:
                return {"error": f"Sketch not found: {sketch_name}"}

            # Create extrusion
            extrude = doc.addObject("Part::Extrusion", f"{sketch_name}_extrude")
            extrude.Base = sketch
            extrude.Dir = App.Vector(*direction)
            extrude.LengthFwd = length
            extrude.Solid = solid
            extrude.Reversed = False
            extrude.Symmetric = False
            extrude.TaperAngle = 0
            extrude.TaperAngleReversed = 0

            doc.recompute()
            return {"name": extrude.Name}
        except Exception as e:
            return {"error": str(e)}

    def boolean_operation(self, operation="union", objects=None, name=None):
        """Perform boolean operation on objects"""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}

        try:
            if not objects or len(objects) < 2:
                return {"error": "At least two objects are required"}

            # Get the objects
            obj_list = [doc.getObject(obj_name) for obj_name in objects]
            if None in obj_list:
                return {"error": "One or more objects not found"}

            # Create boolean operation
            if operation == "union":
                bool_obj = doc.addObject("Part::Fuse", name or "Union")
            elif operation == "cut":
                bool_obj = doc.addObject("Part::Cut", name or "Cut")
            elif operation == "intersection":
                bool_obj = doc.addObject("Part::Common", name or "Intersection")
            else:
                return {"error": f"Unsupported operation: {operation}"}

            bool_obj.Base = obj_list[0]
            bool_obj.Tool = obj_list[1]

            doc.recompute()
            return {"name": bool_obj.Name}
        except Exception as e:
            return {"error": str(e)}

    def fillet_edge(self, object_name, radius, edges=None):
        """Create a fillet on object edges"""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}

        try:
            obj = doc.getObject(object_name)
            if not obj:
                return {"error": f"Object not found: {object_name}"}

            # Create fillet
            fillet = doc.addObject("Part::Fillet", f"{object_name}_fillet")
            fillet.Base = obj
            
            # If no edges specified, fillet all edges
            if edges is None:
                edges = range(len(obj.Shape.Edges))
            
            # Add edges to fillet
            for edge_idx in edges:
                fillet.Edges = [(edge_idx, radius, radius)]

            doc.recompute()
            return {"name": fillet.Name}
        except Exception as e:
            return {"error": str(e)}

    def chamfer_edge(self, object_name, distance, edges=None):
        """Create a chamfer on object edges"""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}

        try:
            obj = doc.getObject(object_name)
            if not obj:
                return {"error": f"Object not found: {object_name}"}

            # Create chamfer
            chamfer = doc.addObject("Part::Chamfer", f"{object_name}_chamfer")
            chamfer.Base = obj
            
            # If no edges specified, chamfer all edges
            if edges is None:
                edges = range(len(obj.Shape.Edges))
            
            # Add edges to chamfer
            for edge_idx in edges:
                chamfer.Edges = [(edge_idx, distance, distance)]

            doc.recompute()
            return {"name": chamfer.Name}
        except Exception as e:
            return {"error": str(e)}

    def create_array(self, object_name, array_type="rectangular",
                    x_count=2, y_count=2, z_count=1,
                    x_spacing=10, y_spacing=10, z_spacing=10,
                    axis=[0,0,1], angle=360, count=4):
        """Create an array of objects"""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}

        try:
            obj = doc.getObject(object_name)
            if not obj:
                return {"error": f"Object not found: {object_name}"}

            if array_type == "rectangular":
                # Create rectangular array
                array = doc.addObject("Part::MultiTransform", f"{object_name}_array")
                array.Base = obj
                
                # Create transformations
                transforms = []
                if x_count > 1:
                    transforms.append(
                        App.Matrix(1,0,0,x_spacing, 0,1,0,0, 0,0,1,0, 0,0,0,1)
                    )
                if y_count > 1:
                    transforms.append(
                        App.Matrix(1,0,0,0, 0,1,0,y_spacing, 0,0,1,0, 0,0,0,1)
                    )
                if z_count > 1:
                    transforms.append(
                        App.Matrix(1,0,0,0, 0,1,0,0, 0,0,1,z_spacing, 0,0,0,1)
                    )
                
                array.Transformations = transforms
                array.Occurrences.x = x_count
                array.Occurrences.y = y_count
                array.Occurrences.z = z_count

            elif array_type == "polar":
                # Create polar array
                array = doc.addObject("Part::MultiTransform", f"{object_name}_array")
                array.Base = obj
                
                # Create rotation transformation
                rot_axis = App.Vector(*axis)
                rot_step = angle / count
                transform = App.Rotation(rot_axis, rot_step).toMatrix()
                array.Transformations = [transform]
                array.Occurrences.x = count
                array.Occurrences.y = 1
                array.Occurrences.z = 1

            else:
                return {"error": f"Unsupported array type: {array_type}"}

            doc.recompute()
            return {"name": array.Name}
        except Exception as e:
            return {"error": str(e)}

    def create_draft_object(self, type="Rectangle", name=None, points=None, properties=None):
        """Create a Draft workbench object"""
        doc = App.ActiveDocument
        if not doc:
            doc = App.newDocument()

        try:
            import Draft
            
            # Create the object based on type
            if type == "Rectangle":
                x = properties.get("x", 0)
                y = properties.get("y", 0)
                length = properties.get("length", 10)
                width = properties.get("width", 10)
                obj = Draft.makeRectangle(length, width, placement=App.Placement(
                    App.Vector(x, y, 0), App.Rotation()
                ))
            elif type == "Circle":
                radius = properties.get("radius", 5)
                center = properties.get("center", [0,0])
                obj = Draft.makeCircle(radius, placement=App.Placement(
                    App.Vector(*center, 0), App.Rotation()
                ))
            elif type == "Polygon":
                if not points:
                    return {"error": "Points required for polygon"}
                obj = Draft.makePolygon(points)
            else:
                return {"error": f"Unsupported draft object type: {type}"}

            if name:
                obj.Label = name

            doc.recompute()
            return {"name": obj.Name}
        except Exception as e:
            return {"error": str(e)}

    def create_constraint(self, sketch_name, constraint_type, elements, value=None):
        """Add a constraint to a sketch"""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}

        try:
            sketch = doc.getObject(sketch_name)
            if not sketch:
                return {"error": f"Sketch not found: {sketch_name}"}

            # Add constraint based on type
            if constraint_type == "distance":
                sketch.addConstraint(Sketcher.Constraint(
                    'Distance', elements[0], elements[1], value
                ))
            elif constraint_type == "angle":
                sketch.addConstraint(Sketcher.Constraint(
                    'Angle', elements[0], elements[1], math.radians(value)
                ))
            elif constraint_type == "parallel":
                sketch.addConstraint(Sketcher.Constraint(
                    'Parallel', elements[0], elements[1]
                ))
            elif constraint_type == "perpendicular":
                sketch.addConstraint(Sketcher.Constraint(
                    'Perpendicular', elements[0], elements[1]
                ))
            elif constraint_type == "horizontal":
                sketch.addConstraint(Sketcher.Constraint(
                    'Horizontal', elements[0]
                ))
            elif constraint_type == "vertical":
                sketch.addConstraint(Sketcher.Constraint(
                    'Vertical', elements[0]
                ))
            else:
                return {"error": f"Unsupported constraint type: {constraint_type}"}

            doc.recompute()
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

    def save_document(self, filename=None):
        """Save the current document"""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}

        try:
            if filename:
                doc.saveAs(filename)
            else:
                doc.save()
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

    def export_object(self, name, filename, format="STEP"):
        """Export an object to a file"""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}

        try:
            obj = doc.getObject(name)
            if not obj:
                return {"error": f"Object not found: {name}"}

            # Export based on format
            if format == "STEP":
                import Import
                Import.export([obj], filename)
            elif format == "IGES":
                import Import
                Import.export([obj], filename)
            elif format == "STL":
                import Mesh
                Mesh.export([obj], filename)
            else:
                return {"error": f"Unsupported export format: {format}"}

            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

class FreeCADMCPPanel:
    def __init__(self):
        self.form = QtGui.QWidget()
        self.form.setWindowTitle("FreeCAD MCP")
        
        layout = QtGui.QVBoxLayout(self.form)
        
        # Server status
        self.status_label = QtGui.QLabel("Server: Stopped")
        layout.addWidget(self.status_label)
        
        # Start/Stop buttons
        button_layout = QtGui.QHBoxLayout()
        self.start_button = QtGui.QPushButton("Start Server")
        self.stop_button = QtGui.QPushButton("Stop Server")
        self.stop_button.setEnabled(False)
        
        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # Server instance
        self.server = None

    def start_server(self):
        if not self.server:
            self.server = FreeCADMCPServer()
            self.server.start()
            self.status_label.setText("Server: Running")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def stop_server(self):
        if self.server:
            self.server.stop()
            self.server = None
            self.status_label.setText("Server: Stopped")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

def show_panel():
    panel = FreeCADMCPPanel()
    Gui.Control.showDialog(panel) 