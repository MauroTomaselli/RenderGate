"""RenderGate Import Operator.
Standard Blender File Browser import operator using bpy_extras.io_utils.ImportHelper.
Loads a .RGE preset, applies settings, and alerts the user to any cross-version discrepancies.
"""

import os
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from ..core import load_rge_file, SceneDeserializer


class RENDER_OT_rendergate_import(bpy.types.Operator, ImportHelper):
    """Import and apply render settings from a .RGE preset file"""

    bl_idname = "render.rendergate_import"
    bl_label = "Import RenderGate Preset (.RGE)"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".RGE"
    filter_glob: StringProperty(
        default="*.RGE;*.rge",
        options={"HIDDEN"},
        maxlen=255,
    )

    # Category import toggles
    apply_dimensions: BoolProperty(
        name="Dimensions & Framing",
        description="Apply resolution, aspect ratio, frame rate, and border settings",
        default=True,
    )
    apply_engine: BoolProperty(
        name="Render Engine & General",
        description="Apply render engine selection, film transparency, and simplify",
        default=True,
    )
    apply_color: BoolProperty(
        name="Color Management",
        description="Apply view transform (AgX/Filmic), look, exposure, gamma",
        default=True,
    )
    apply_cycles: BoolProperty(
        name="Cycles Settings",
        description="Apply Cycles samples, denoising, light bounces, caustics, etc.",
        default=True,
    )
    apply_eevee: BoolProperty(
        name="EEVEE Settings",
        description="Apply EEVEE / EEVEE Next raytracing, shadows, and GI settings",
        default=True,
    )
    apply_output: BoolProperty(
        name="Output Format",
        description="Apply file format, color depth, compression, and quality",
        default=True,
    )
    apply_passes: BoolProperty(
        name="View Layer Passes",
        description="Apply view layer render passes",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        box_cats = layout.box()
        box_cats.label(text="Categories to Apply", icon="FILTER")
        box_cats.prop(self, "apply_dimensions")
        box_cats.prop(self, "apply_engine")
        box_cats.prop(self, "apply_color")
        box_cats.prop(self, "apply_cycles")
        box_cats.prop(self, "apply_eevee")
        box_cats.prop(self, "apply_output")
        box_cats.prop(self, "apply_passes")

    def execute(self, context):
        success, preset_data, err_or_path = load_rge_file(self.filepath)
        if not success:
            self.report({"ERROR"}, f"RenderGate: {err_or_path}")
            return {"CANCELLED"}

        selected_categories = []
        if self.apply_dimensions:
            selected_categories.append("dimensions")
        if self.apply_engine:
            selected_categories.append("engine")
        if self.apply_color:
            selected_categories.append("color_management")
        if self.apply_cycles:
            selected_categories.append("cycles")
        if self.apply_eevee:
            selected_categories.append("eevee")
        if self.apply_output:
            selected_categories.append("output_format")
        if self.apply_passes:
            selected_categories.append("passes")

        deserializer = SceneDeserializer(context.scene, view_layer=context.view_layer)
        report = deserializer.apply_preset_dict(
            preset_data,
            preset_name=os.path.splitext(os.path.basename(self.filepath))[0],
            file_path=self.filepath,
            category_filter=selected_categories,
        )

        preset_blender_ver = report.source_blender_version
        applied_count = len(report.applied)
        skipped_count = len(report.skipped)

        if report.has_warnings:
            self.report(
                {"WARNING"},
                f"RenderGate: Applied {applied_count} settings ({skipped_count} skipped/incompatible from Blender {preset_blender_ver}). Open report for details.",
            )
            # Open report dialog
            try:
                bpy.ops.render.rendergate_show_report("INVOKE_DEFAULT")
            except Exception:
                pass
        else:
            self.report(
                {"INFO"},
                f"RenderGate: Successfully applied all {applied_count} render settings from '{os.path.basename(self.filepath)}'",
            )

        return {"FINISHED"}
