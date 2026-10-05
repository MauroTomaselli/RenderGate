"""RenderGate Deserializer.
Applies settings from a .RGE preset safely to a Blender scene,
handling cross-version differences, validating enums, and collecting a detailed compatibility report.
"""

from typing import Dict, Any, List, Optional, Tuple
import bpy
from .report import RenderGateReport, SettingResult
from .compat import get_compatibility_hint


def _resolve_target(
    scene: bpy.types.Scene,
    view_layer: bpy.types.ViewLayer,
    field_path: str,
) -> Tuple[Optional[Any], Optional[str], Optional[str]]:
    """Resolves a field path like 'scene.cycles.samples' into (target_obj, prop_name, error_reason)."""
    parts = field_path.split(".")
    if len(parts) < 2:
        return None, None, f"Malformed field path: '{field_path}'"

    root_name = parts[0]
    if root_name == "scene":
        curr = scene
    elif root_name == "view_layer":
        curr = view_layer
    else:
        return None, None, f"Unknown root object: '{root_name}'"

    for part in parts[1:-1]:
        if not hasattr(curr, part):
            return None, None, f"Sub-object '{part}' not found on '{curr}'"
        curr = getattr(curr, part)
        if curr is None:
            return None, None, f"Sub-object '{part}' is None"

    prop_name = parts[-1]
    return curr, prop_name, None


class SceneDeserializer:
    """Safely applies preset settings to a Blender scene with version compatibility handling."""

    def __init__(self, scene: bpy.types.Scene, view_layer: Optional[bpy.types.ViewLayer] = None):
        self.scene = scene
        self.view_layer = view_layer or getattr(bpy.context, "view_layer", None) or scene.view_layers[0]

    def apply_preset_dict(
        self,
        preset_data: Dict[str, Any],
        preset_name: str = "Unknown Preset",
        file_path: str = "",
        category_filter: Optional[List[str]] = None,
    ) -> RenderGateReport:
        """Applies a preset dictionary and returns the compatibility report."""
        meta = preset_data.get("_rendergate_meta", {})
        source_ver = meta.get("blender_version_str") or ".".join(str(x) for x in meta.get("blender_version", []))
        if not source_ver:
            source_ver = "Unknown"

        report = RenderGateReport(
            preset_name=preset_name or meta.get("preset_name", "Preset"),
            file_path=file_path,
            source_blender_version=source_ver,
        )

        categories = preset_data.get("categories", {})
        allowed_categories = set(category_filter) if category_filter else None

        # First, if the 'engine' category is present, apply render.engine FIRST
        # because other properties (like cycles or eevee) depend on the active engine!
        if "engine" in categories and (allowed_categories is None or "engine" in allowed_categories):
            self._apply_category(categories["engine"], report)

        # Then apply the remaining categories
        for cat_id, cat_content in categories.items():
            if cat_id == "engine":
                continue  # already applied
            if allowed_categories is not None and cat_id not in allowed_categories:
                continue
            self._apply_category(cat_content, report)

        # Store as last report
        RenderGateReport.set_last_report(report)
        return report

    def _apply_category(self, cat_dict: Dict[str, Any], report: RenderGateReport) -> None:
        cat_label = cat_dict.get("category_label", "General")
        properties = cat_dict.get("properties", [])

        for prop_info in properties:
            field = prop_info.get("field", "")
            label = prop_info.get("label", field)
            value = prop_info.get("value")

            if not field:
                continue

            target_obj, prop_name, err = _resolve_target(self.scene, self.view_layer, field)
            if target_obj is None or not prop_name:
                hint = get_compatibility_hint(field)
                reason = f"Target object path not found in Blender {bpy.app.version_string}."
                if hint:
                    reason += f" Note: {hint}"
                report.add_result(
                    field=field,
                    label=label,
                    value=value,
                    status=SettingResult.STATUS_SKIPPED_MISSING,
                    reason=reason,
                    category=cat_label,
                )
                continue

            # Check if property exists on target object
            if not hasattr(target_obj, prop_name):
                hint = get_compatibility_hint(field)
                reason = f"Property '{prop_name}' does not exist in Blender {bpy.app.version_string}."
                if hint:
                    reason += f" Note: {hint}"
                report.add_result(
                    field=field,
                    label=label,
                    value=value,
                    status=SettingResult.STATUS_SKIPPED_MISSING,
                    reason=reason,
                    category=cat_label,
                )
                continue

            # Check RNA property metadata if available
            prop_rna = None
            if hasattr(target_obj, "bl_rna"):
                prop_rna = target_obj.bl_rna.properties.get(prop_name)

            if prop_rna and prop_rna.is_readonly:
                report.add_result(
                    field=field,
                    label=label,
                    value=value,
                    status=SettingResult.STATUS_SKIPPED_MISSING,
                    reason="Property is read-only in this context.",
                    category=cat_label,
                )
                continue

            # Perform assignment with robust exception handling
            try:
                is_array = getattr(prop_rna, "is_array", False)
                if is_array and isinstance(value, list):
                    setattr(target_obj, prop_name, tuple(value))
                else:
                    setattr(target_obj, prop_name, value)

                report.add_result(
                    field=field,
                    label=label,
                    value=value,
                    status=SettingResult.STATUS_APPLIED,
                    category=cat_label,
                )
            except TypeError as te:
                err_msg = str(te)
                hint = get_compatibility_hint(field)
                if "not found in" in err_msg and "enum" in err_msg:
                    reason = f"Option '{value}' is not supported in Blender {bpy.app.version_string} ({err_msg})."
                    if hint:
                        reason += f" Note: {hint}"
                    report.add_result(
                        field=field,
                        label=label,
                        value=value,
                        status=SettingResult.STATUS_SKIPPED_INVALID_ENUM,
                        reason=reason,
                        category=cat_label,
                    )
                else:
                    reason = f"Type or configuration error in Blender {bpy.app.version_string}: {err_msg}"
                    if hint:
                        reason += f" Note: {hint}"
                    report.add_result(
                        field=field,
                        label=label,
                        value=value,
                        status=SettingResult.STATUS_FAILED,
                        reason=reason,
                        category=cat_label,
                    )
            except AttributeError as ae:
                hint = get_compatibility_hint(field)
                reason = f"Attribute error: {str(ae)}"
                if hint:
                    reason += f" Note: {hint}"
                report.add_result(
                    field=field,
                    label=label,
                    value=value,
                    status=SettingResult.STATUS_SKIPPED_MISSING,
                    reason=reason,
                    category=cat_label,
                )
            except Exception as e:
                hint = get_compatibility_hint(field)
                reason = str(e)
                if hint:
                    reason += f" Note: {hint}"
                report.add_result(
                    field=field,
                    label=label,
                    value=value,
                    status=SettingResult.STATUS_FAILED,
                    reason=reason,
                    category=cat_label,
                )
