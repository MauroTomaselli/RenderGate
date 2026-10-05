"""RenderGate UI Panel.
Located in Properties Editor -> Render Properties tab.
Provides preset dropdown, save/delete, import/export buttons, and quick compatibility reports.
"""

import bpy
from bpy.props import EnumProperty, BoolProperty, PointerProperty
from ..operators.preset_ops import preset_items_callback
from ..core.report import RenderGateReport


class RenderGateSceneProperties(bpy.types.PropertyGroup):
    """Properties stored per scene for RenderGate configuration."""

    active_preset: EnumProperty(
        name="Preset",
        description="Select a RenderGate preset to apply or manage",
        items=preset_items_callback,
    )

    auto_open_report_on_warning: BoolProperty(
        name="Auto-Show Warnings",
        description="Automatically open the compatibility report dialog if any setting was skipped",
        default=True,
    )


class RENDER_PT_rendergate(bpy.types.Panel):
    """RenderGate presets management panel in Render Properties"""

    bl_label = "RenderGate Presets"
    bl_idname = "RENDER_PT_rendergate"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_order = 0  # Show at the top of the Render tab

    def draw_header(self, context):
        self.layout.label(text="", icon="PRESET")

    def draw(self, context):
        layout = self.layout
        props = context.scene.rendergate_props

        # Preset selection row with + and -
        box_presets = layout.box()
        box_presets.label(text="Preset Library (.RGE)", icon="PRESET_NEW")

        row = box_presets.row(align=True)
        row.prop(props, "active_preset", text="")
        row.operator("render.rendergate_preset_save", text="", icon="ADD")
        row.operator("render.rendergate_preset_remove", text="", icon="REMOVE")

        row_apply = box_presets.row()
        row_apply.scale_y = 1.3
        row_apply.operator("render.rendergate_preset_apply", text="Apply Selected Preset", icon="CHECKMARK")

        # Import & Export Buttons
        box_io = layout.box()
        box_io.label(text="File Browser I/O", icon="FILE_FOLDER")
        row_io = box_io.row(align=True)
        row_io.scale_y = 1.1
        row_io.operator("render.rendergate_import", text="Import .RGE...", icon="IMPORT")
        row_io.operator("render.rendergate_export", text="Export .RGE...", icon="EXPORT")

        # Report & Utilities Box
        report = RenderGateReport.get_last_report()
        box_status = layout.box()
        box_status.label(text="Preset Compatibility", icon="INFO")

        if report:
            col_info = box_status.column(align=True)
            row_stats = col_info.row(align=True)
            row_stats.label(text=f"Loaded: {report.preset_name}")
            row_stats.label(text=f"Src: {report.source_blender_version}")

            row_counts = col_info.row(align=True)
            row_counts.label(text=f"Applied: {len(report.applied)}", icon="CHECKBOX_HLT")
            if report.has_warnings:
                row_counts.label(text=f"Skipped: {len(report.skipped)}", icon="ERROR")

            row_btn = box_status.row()
            row_btn.operator("render.rendergate_show_report", text="View Compatibility Report", icon="TEXT")
        else:
            box_status.label(text="No preset loaded in this session.", icon="BLANK1")

        # Presets Folder quick link
        row_footer = layout.row()
        row_footer.alignment = "RIGHT"
        row_footer.operator("render.rendergate_open_preset_dir", text="Open Presets Folder", icon="FOLDER_REDIRECT")
