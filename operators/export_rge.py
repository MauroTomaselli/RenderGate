"""RenderGate Export Operator.
Standard Blender File Browser export operator using bpy_extras.io_utils.ExportHelper.
Exports render settings to a human-readable .RGE file.
"""

import os
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from ..core import SceneSerializer, save_rge_file


class RENDER_OT_rendergate_export(bpy.types.Operator, ExportHelper):
    """Export current scene render settings to a .RGE preset file"""

    bl_idname = "render.rendergate_export"
    bl_label = "Export RenderGate Preset (.RGE)"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".RGE"
    filter_glob: StringProperty(
        default="*.RGE;*.rge",
        options={"HIDDEN"},
        maxlen=255,
    )

    preset_name: StringProperty(
        name="Preset Name",
        description="Name identifier for this preset",
        default="My Render Preset",
    )
    preset_notes: StringProperty(
        name="Description",
        description="Optional notes describing this preset",
        default="",
    )

    # Category export toggles
    include_dimensions: BoolProperty(
        name="Dimensions & Framing",
        description="Include resolution, aspect ratio, frame rate, and border settings",
        default=True,
    )
    include_engine: BoolProperty(
        name="Render Engine & General",
        description="Include render engine selection, film transparency, and simplify",
        default=True,
    )
    include_color: BoolProperty(
        name="Color Management",
        description="Include view transform (AgX/Filmic), look, exposure, gamma",
        default=True,
    )
    include_cycles: BoolProperty(
        name="Cycles Settings",
        description="Include Cycles samples, denoising, light bounces, caustics, etc.",
        default=True,
    )
    include_eevee: BoolProperty(
        name="EEVEE Settings",
        description="Include EEVEE / EEVEE Next raytracing, shadows, and GI settings",
        default=True,
    )
    include_output: BoolProperty(
        name="Output Format",
        description="Include file format, color depth, compression, and quality",
        default=True,
    )
    include_passes: BoolProperty(
        name="View Layer Passes",
        description="Include active view layer render passes",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        box_meta = layout.box()
        box_meta.label(text="Preset Metadata", icon="INFO")
        box_meta.prop(self, "preset_name")
        box_meta.prop(self, "preset_notes")

        box_cats = layout.box()
        box_cats.label(text="Categories to Include", icon="FILTER")
        box_cats.prop(self, "include_dimensions")
        box_cats.prop(self, "include_engine")
        box_cats.prop(self, "include_color")
        box_cats.prop(self, "include_cycles")
        box_cats.prop(self, "include_eevee")
        box_cats.prop(self, "include_output")
        box_cats.prop(self, "include_passes")

    def execute(self, context):
        scene = context.scene
        serializer = SceneSerializer(scene, view_layer=context.view_layer)

        selected_categories = []
        if self.include_dimensions:
            selected_categories.append("dimensions")
        if self.include_engine:
            selected_categories.append("engine")
        if self.include_color:
            selected_categories.append("color_management")
        if self.include_cycles:
            selected_categories.append("cycles")
        if self.include_eevee:
            selected_categories.append("eevee")
        if self.include_output:
            selected_categories.append("output_format")
        if self.include_passes:
            selected_categories.append("passes")

        preset_data = serializer.serialize_all(
            preset_name=self.preset_name or os.path.splitext(os.path.basename(self.filepath))[0],
            description=self.preset_notes,
            categories=selected_categories,
        )

        success, msg = save_rge_file(self.filepath, preset_data)
        if not success:
            self.report({"ERROR"}, msg)
            return {"CANCELLED"}

        self.report({"INFO"}, f"RenderGate: Preset saved successfully to '{os.path.basename(self.filepath)}'")
        return {"FINISHED"}
