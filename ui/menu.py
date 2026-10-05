"""RenderGate Menu Integration.
Registers RenderGate in Blender's standard File > Export and File > Import topbar menus.
"""

import bpy


def menu_func_export(self, context):
    self.layout.operator("render.rendergate_export", text="RenderGate Preset (.RGE)")


def menu_func_import(self, context):
    self.layout.operator("render.rendergate_import", text="RenderGate Preset (.RGE)")


def register_menus():
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister_menus():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
