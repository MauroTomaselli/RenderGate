"""RenderGate Operators Package."""

from .export_rge import RENDER_OT_rendergate_export
from .import_rge import RENDER_OT_rendergate_import
from .preset_ops import (
    RENDER_OT_rendergate_preset_save,
    RENDER_OT_rendergate_preset_remove,
    RENDER_OT_rendergate_preset_apply,
    RENDER_OT_rendergate_open_preset_dir,
    preset_items_callback,
)
from .report_ops import (
    RENDER_OT_rendergate_show_report,
    RENDER_OT_rendergate_copy_report,
    RENDER_OT_rendergate_log_to_text,
)

OPERATOR_CLASSES = [
    RENDER_OT_rendergate_export,
    RENDER_OT_rendergate_import,
    RENDER_OT_rendergate_preset_save,
    RENDER_OT_rendergate_preset_remove,
    RENDER_OT_rendergate_preset_apply,
    RENDER_OT_rendergate_open_preset_dir,
    RENDER_OT_rendergate_show_report,
    RENDER_OT_rendergate_copy_report,
    RENDER_OT_rendergate_log_to_text,
]
