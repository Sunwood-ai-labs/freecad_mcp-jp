import FreeCAD as App
import FreeCADGui as Gui
import os

def create_freecad_mcp_command():
    class FreeCADMCPShowCommand:
        """Command to show the FreeCAD MCP panel"""
        
        def GetResources(self):
            user_dir = App.getUserAppDataDir()
            icon_path = os.path.join(user_dir, "Mod", "freecad_mcp", "assets", "icon.svg")
            return {
                'Pixmap': icon_path,
                'MenuText': 'Show FreeCAD MCP Panel',
                'ToolTip': 'Show the FreeCAD Model Control Protocol panel'
            }
            
        def IsActive(self):
            return True
            
        def Activated(self):
            import freecad_mcp
            freecad_mcp.show_panel()

    return FreeCADMCPShowCommand()

# Add the command to FreeCAD
if not hasattr(Gui, "freecad_mcp_command"):
    Gui.freecad_mcp_command = create_freecad_mcp_command()
    Gui.addCommand('FreeCAD_MCP_Show', Gui.freecad_mcp_command) 