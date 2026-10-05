"""RenderGate - Blender Render Settings Preset Manager.
Allows saving all render settings to human-readable .RGE files,
loading presets, and handling cross-version compatibility gracefully.
"""

bl_info = {
    "name": "RenderGate",
    "author": "RenderGate Team",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "Properties > Render > RenderGate Presets & File > Import/Export",
    "description": "Save and load comprehensive render presets in human-readable .RGE files with cross-version compatibility",
    "warning": "",
    "doc_url": "",
    "category": "Render",
}

import bpy
from bpy.props import PointerProperty

from .operators import OPERATOR_CLASSES
from .ui import UI_CLASSES, RenderGateSceneProperties, register_menus, unregister_menus


def register():
    # Register operator classes
    for cls in OPERATOR_CLASSES:
        bpy.utils.register_class(cls)

    # Register UI classes
    for cls in UI_CLASSES:
        bpy.utils.register_class(cls)

    # Attach properties to Scene
    bpy.types.Scene.rendergate_props = PointerProperty(type=RenderGateSceneProperties)

    # Register topbar menus
    register_menus()


def unregister():
    # Unregister topbar menus
    unregister_menus()

    # Remove scene property pointer
    if hasattr(bpy.types.Scene, "rendergate_props"):
        del bpy.types.Scene.rendergate_props

    # Unregister UI classes in reverse order
    for cls in reversed(UI_CLASSES):
        bpy.utils.unregister_class(cls)

    # Unregister operator classes in reverse order
    for cls in reversed(OPERATOR_CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
