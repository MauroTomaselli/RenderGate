"""RenderGate Preset Management Operators.
Handles Blender standard preset folder integration: saving, removing,
listing, and applying presets directly from the user's scripts/presets directory.
"""

import os
import bpy
from bpy.props import StringProperty, EnumProperty
from ..core import (
    SceneSerializer,
    SceneDeserializer,
    save_rge_file,
    load_rge_file,
    RGE_EXTENSION,
)


def get_user_preset_dir() -> str:
    """Returns the user scripts preset directory for RenderGate."""
    preset_dir = bpy.utils.user_resource("SCRIPTS", path="presets/rendergate", create=True)
    if not os.path.exists(preset_dir):
        os.makedirs(preset_dir, exist_ok=True)
    return preset_dir


def get_bundled_preset_dir() -> str:
    """Returns the directory containing built-in presets shipped with RenderGate."""
    addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(addon_dir, "presets")


def get_preset_files() -> list:
    """Enumerates all .RGE files from both user preset directory and bundled presets."""
    preset_files = []
    seen_names = set()

    # 1. User presets (priority)
    user_dir = get_user_preset_dir()
    if os.path.exists(user_dir):
        for f in sorted(os.listdir(user_dir)):
            if f.upper().endswith(RGE_EXTENSION):
                name = os.path.splitext(f)[0]
                preset_files.append((os.path.join(user_dir, f), name, "User Preset"))
                seen_names.add(name)

    # 2. Bundled presets
    bundled_dir = get_bundled_preset_dir()
    if os.path.exists(bundled_dir):
        for f in sorted(os.listdir(bundled_dir)):
            if f.upper().endswith(RGE_EXTENSION):
                name = os.path.splitext(f)[0]
                if name not in seen_names:
                    preset_files.append((os.path.join(bundled_dir, f), name, "Built-in Preset"))
                    seen_names.add(name)

    return preset_files


def preset_items_callback(self, context):
    """Dynamic EnumProperty callback listing available .RGE presets."""
    items = []
    presets = get_preset_files()

    if not presets:
        return [("NONE", "No presets available", "No .RGE files found")]

    for idx, (path, name, desc) in enumerate(presets):
        icon = "PRESET" if "Built-in" in desc else "FILE_TEXT"
        items.append((path, name, f"{desc}: {path}", icon, idx))

    return items


class RENDER_OT_rendergate_preset_save(bpy.types.Operator):
    """Save current scene render settings as a standard preset"""

    bl_idname = "render.rendergate_preset_save"
    bl_label = "Save RenderGate Preset"
    bl_options = {"REGISTER", "UNDO"}

    preset_name: StringProperty(
        name="Preset Name",
        description="Name for the new preset",
        default="New_Render_Preset",
    )
    preset_notes: StringProperty(
        name="Description",
        description="Optional notes",
        default="",
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")
        layout.prop(self, "preset_notes")

    def execute(self, context):
        name = self.preset_name.strip()
        if not name:
            self.report({"ERROR"}, "Preset name cannot be empty.")
            return {"CANCELLED"}

        # Sanitize filename
        clean_name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip()
        filename = clean_name + RGE_EXTENSION
        target_path = os.path.join(get_user_preset_dir(), filename)

        serializer = SceneSerializer(context.scene, view_layer=context.view_layer)
        data = serializer.serialize_all(
            preset_name=clean_name,
            description=self.preset_notes,
        )

        success, msg = save_rge_file(target_path, data)
        if not success:
            self.report({"ERROR"}, msg)
            return {"CANCELLED"}

        self.report({"INFO"}, f"RenderGate: Saved preset '{clean_name}'")
        # Update active preset property if available
        context.scene.rendergate_props.active_preset = target_path
        return {"FINISHED"}


class RENDER_OT_rendergate_preset_remove(bpy.types.Operator):
    """Remove the currently selected preset from the user presets folder"""

    bl_idname = "render.rendergate_preset_remove"
    bl_label = "Delete Selected Preset"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        props = context.scene.rendergate_props
        if not props.active_preset or props.active_preset == "NONE" or not os.path.isfile(props.active_preset):
            self.report({"WARNING"}, "No valid preset selected to delete.")
            return {"CANCELLED"}

        user_dir = os.path.abspath(get_user_preset_dir())
        target_dir = os.path.abspath(os.path.dirname(props.active_preset))
        if user_dir != target_dir:
            self.report({"WARNING"}, "Built-in presets cannot be deleted.")
            return {"CANCELLED"}

        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        props = context.scene.rendergate_props
        preset_path = props.active_preset

        if not os.path.isfile(preset_path):
            self.report({"ERROR"}, "Preset file not found.")
            return {"CANCELLED"}

        try:
            os.remove(preset_path)
            self.report({"INFO"}, f"RenderGate: Deleted preset '{os.path.basename(preset_path)}'")
            remaining = get_preset_files()
            if remaining:
                props.active_preset = remaining[0][0]
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"Could not delete preset: {str(e)}")
            return {"CANCELLED"}


class RENDER_OT_rendergate_preset_apply(bpy.types.Operator):
    """Apply the selected RenderGate preset to the current scene"""

    bl_idname = "render.rendergate_preset_apply"
    bl_label = "Apply Selected Preset"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.rendergate_props
        preset_path = props.active_preset

        if not preset_path or preset_path == "NONE" or not os.path.isfile(preset_path):
            self.report({"WARNING"}, "No valid preset selected to apply.")
            return {"CANCELLED"}

        success, preset_data, err_or_path = load_rge_file(preset_path)
        if not success:
            self.report({"ERROR"}, f"RenderGate: {err_or_path}")
            return {"CANCELLED"}

        deserializer = SceneDeserializer(context.scene, view_layer=context.view_layer)
        report = deserializer.apply_preset_dict(
            preset_data,
            preset_name=os.path.splitext(os.path.basename(preset_path))[0],
            file_path=preset_path,
        )

        preset_blender_ver = report.source_blender_version
        applied_count = len(report.applied)
        skipped_count = len(report.skipped)

        if report.has_warnings:
            self.report(
                {"WARNING"},
                f"RenderGate: Applied {applied_count} settings ({skipped_count} skipped from Blender {preset_blender_ver}). Open report for details.",
            )
            try:
                bpy.ops.render.rendergate_show_report("INVOKE_DEFAULT")
            except Exception:
                pass
        else:
            self.report(
                {"INFO"},
                f"RenderGate: Successfully applied '{os.path.basename(preset_path)}' ({applied_count} settings)",
            )

        return {"FINISHED"}


class RENDER_OT_rendergate_open_preset_dir(bpy.types.Operator):
    """Open the RenderGate preset directory in the system file manager"""

    bl_idname = "render.rendergate_open_preset_dir"
    bl_label = "Open Presets Folder"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        preset_dir = get_user_preset_dir()
        bpy.ops.wm.path_open(filepath=preset_dir)
        return {"FINISHED"}
