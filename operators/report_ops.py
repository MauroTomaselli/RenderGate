"""RenderGate Compatibility Report Operators.
Provides visual feedback on preset loading, showing version differences and reasons for skipped settings.
"""

import bpy
from ..core import RenderGateReport


class RENDER_OT_rendergate_show_report(bpy.types.Operator):
    """Show detailed compatibility and import report for the last loaded preset"""

    bl_idname = "render.rendergate_show_report"
    bl_label = "RenderGate Compatibility Report"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        report = RenderGateReport.get_last_report()
        if not report:
            self.report({"INFO"}, "No RenderGate report available yet.")
            return {"CANCELLED"}
        return context.window_manager.invoke_props_dialog(self, width=580)

    def draw(self, context):
        layout = self.layout
        report = RenderGateReport.get_last_report()
        if not report:
            layout.label(text="No report available.")
            return

        box_head = layout.box()
        row = box_head.row()
        row.label(text=f"Preset: {report.preset_name}", icon="FILE_TEXT")
        row = box_head.row()
        row.label(text=f"Origin Version: {report.source_blender_version}", icon="BLENDER")
        row.label(text=f"Current: {report.current_blender_version}", icon="CHECKMARK")

        row = layout.row(align=True)
        row.label(text=f"Applied: {len(report.applied)}", icon="CHECKBOX_HLT")
        if report.skipped:
            row.label(text=f"Incompatible: {len(report.skipped)}", icon="ERROR")
        if report.failed:
            row.label(text=f"Errors: {len(report.failed)}", icon="CANCEL")

        if report.skipped:
            box_skip = layout.box()
            box_skip.label(text=f"Incompatible / Skipped Values ({len(report.skipped)}):", icon="INFO")
            col = box_skip.column(align=True)
            for item in report.skipped[:15]:
                sub_box = col.box()
                r1 = sub_box.row()
                r1.label(text=f"{item.label} [{item.category}]", icon="FORWARD")
                r1.label(text=f"Value: {repr(item.value)}")
                r2 = sub_box.row()
                r2.scale_y = 0.8
                r2.label(text=f"Reason: {item.reason}", icon="BLANK1")

            if len(report.skipped) > 15:
                col.label(text=f"... and {len(report.skipped) - 15} more items (see Text Editor for full log).")

        row_actions = layout.row(align=True)
        row_actions.operator("render.rendergate_copy_report", text="Copy to Clipboard", icon="COPYDOWN")
        row_actions.operator("render.rendergate_log_to_text", text="Send to Text Editor", icon="TEXT")

    def execute(self, context):
        return {"FINISHED"}


class RENDER_OT_rendergate_copy_report(bpy.types.Operator):
    """Copy the full RenderGate compatibility report to system clipboard"""

    bl_idname = "render.rendergate_copy_report"
    bl_label = "Copy Report to Clipboard"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        report = RenderGateReport.get_last_report()
        if not report:
            self.report({"WARNING"}, "No report available to copy.")
            return {"CANCELLED"}

        context.window_manager.clipboard = report.format_text_report()
        self.report({"INFO"}, "RenderGate: Full report copied to clipboard.")
        return {"FINISHED"}


class RENDER_OT_rendergate_log_to_text(bpy.types.Operator):
    """Export the report into Blender's internal Text Editor"""

    bl_idname = "render.rendergate_log_to_text"
    bl_label = "Send Report to Text Editor"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        report = RenderGateReport.get_last_report()
        if not report:
            self.report({"WARNING"}, "No report available.")
            return {"CANCELLED"}

        text_name = "RenderGate_Report.txt"
        text_block = bpy.data.texts.get(text_name) or bpy.data.texts.new(name=text_name)
        text_block.clear()
        text_block.write(report.format_text_report())

        self.report({"INFO"}, f"RenderGate: Report written to Blender Text Block '{text_name}'")
        return {"FINISHED"}
