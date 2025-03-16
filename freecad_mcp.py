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
        if not self.running:
            return
            
        try:
            if not self.client and self.socket:
                try:
                    self.client, address = self.socket.accept()
                    self.client.setblocking(False)
                    App.Console.PrintMessage(f"Connected to client: {address}\n")
                except BlockingIOError:
                    pass
                except Exception as e:
                    App.Console.PrintError(f"Error accepting connection: {str(e)}\n")
                
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
        try:
            cmd_type = command.get("type")
            params = command.get("params", {})
            
            handlers = {
                "send_command": self.handle_send_command,
                "run_script": self.handle_run_script
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

    def handle_send_command(self, command, get_context=True):
        """Handle a send_command request with document context"""
        try:
            # Execute the command
            exec(command, {"App": App, "Gui": Gui})
            
            # Get document context if requested
            context = {}
            if get_context:
                context = self.get_document_context()
            
            return {
                "command_result": "success",
                "context": context
            }
        except Exception as e:
            return {
                "command_result": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def handle_run_script(self, script):
        """Handle a run_script request"""
        try:
            # Create a new local namespace for the script
            namespace = {
                "App": App,
                "Gui": Gui,
                "doc": App.ActiveDocument
            }
            
            # Execute the script
            exec(script, namespace)
            
            return {
                "script_result": "success"
            }
        except Exception as e:
            return {
                "script_result": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def get_document_context(self):
        """Get comprehensive information about the current document state"""
        doc = App.ActiveDocument
        if not doc:
            return {
                "document": None,
                "objects": [],
                "view": None
            }

        # Document info
        doc_info = {
            "name": doc.Name,
            "filename": doc.FileName if hasattr(doc, "FileName") else None,
            "object_count": len(doc.Objects)
        }

        # Objects info
        objects = []
        for obj in doc.Objects:
            obj_info = {
                "name": obj.Name,
                "label": obj.Label,
                "type": obj.TypeId,
                "visibility": obj.ViewObject.Visibility if hasattr(obj, "ViewObject") else None
            }
            
            # Add placement if available
            if hasattr(obj, "Placement"):
                pos = obj.Placement.Base
                rot = obj.Placement.Rotation
                obj_info["placement"] = {
                    "position": [float(pos.x), float(pos.y), float(pos.z)],
                    "rotation": [float(rot.Axis.x), float(rot.Axis.y), float(rot.Axis.z), float(rot.Angle)]
                }
            
            # Add shape properties if available
            if hasattr(obj, "Shape"):
                shape = obj.Shape
                obj_info["shape"] = {
                    "type": shape.ShapeType,
                    "volume": float(shape.Volume) if hasattr(shape, "Volume") else None,
                    "area": float(shape.Area) if hasattr(shape, "Area") else None
                }
            
            objects.append(obj_info)

        # View state
        view_info = None
        if Gui.ActiveDocument:
            cam = Gui.ActiveDocument.ActiveView.getCameraNode()
            view_info = {
                "camera_type": cam.getTypeId(),
                "camera_position": [float(x) for x in cam.position.getValue()],
                "camera_orientation": [float(x) for x in cam.orientation.getValue()]
            }

        return {
            "document": doc_info,
            "objects": objects,
            "view": view_info
        }

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