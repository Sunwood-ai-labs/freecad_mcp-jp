import os
import FreeCAD as App
import FreeCADGui as Gui
import json
import socket
import threading
import time
import traceback
from PySide import QtCore, QtGui

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