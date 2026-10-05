"""RenderGate Report Module.
Tracks the result of importing a .RGE preset, documenting applied settings,
skipped/incompatible properties, and version differences.
"""

from typing import List, Dict, Any, Optional
import datetime
import bpy


class SettingResult:
    STATUS_APPLIED = "APPLIED"
    STATUS_SKIPPED_MISSING = "SKIPPED_MISSING"
    STATUS_SKIPPED_INVALID_ENUM = "SKIPPED_INVALID_ENUM"
    STATUS_FAILED = "FAILED"

    def __init__(
        self,
        field: str,
        label: str,
        value: Any,
        status: str,
        reason: str = "",
        category: str = "",
    ):
        self.field = field
        self.label = label
        self.value = value
        self.status = status
        self.reason = reason
        self.category = category

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "label": self.label,
            "value": self.value,
            "status": self.status,
            "reason": self.reason,
            "category": self.category,
        }


class RenderGateReport:
    """Stores the complete outcome of a preset import operation."""

    _last_report: Optional["RenderGateReport"] = None

    def __init__(
        self,
        preset_name: str,
        file_path: str,
        source_blender_version: Optional[str] = None,
    ):
        self.preset_name = preset_name
        self.file_path = file_path
        self.source_blender_version = source_blender_version or "Unknown"
        self.current_blender_version = bpy.app.version_string
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.results: List[SettingResult] = []

    def add_result(
        self,
        field: str,
        label: str,
        value: Any,
        status: str,
        reason: str = "",
        category: str = "",
    ) -> None:
        self.results.append(
            SettingResult(
                field=field,
                label=label,
                value=value,
                status=status,
                reason=reason,
                category=category,
            )
        )

    @property
    def applied(self) -> List[SettingResult]:
        return [r for r in self.results if r.status == SettingResult.STATUS_APPLIED]

    @property
    def skipped(self) -> List[SettingResult]:
        return [
            r
            for r in self.results
            if r.status in (SettingResult.STATUS_SKIPPED_MISSING, SettingResult.STATUS_SKIPPED_INVALID_ENUM)
        ]

    @property
    def failed(self) -> List[SettingResult]:
        return [r for r in self.results if r.status == SettingResult.STATUS_FAILED]

    @property
    def has_warnings(self) -> bool:
        return len(self.skipped) > 0 or len(self.failed) > 0

    @classmethod
    def set_last_report(cls, report: "RenderGateReport") -> None:
        cls._last_report = report

    @classmethod
    def get_last_report(cls) -> Optional["RenderGateReport"]:
        return cls._last_report

    def format_text_report(self) -> str:
        """Generates a clean, readable text report for UI, log files, or text datablock."""
        lines = [
            "============================================================",
            f"          RenderGate Import & Compatibility Report          ",
            "============================================================",
            f"Preset Name:            {self.preset_name}",
            f"File Path:              {self.file_path}",
            f"Preset Blender Version: {self.source_blender_version}",
            f"Current Blender Version:{self.current_blender_version}",
            f"Import Timestamp:       {self.timestamp}",
            "------------------------------------------------------------",
            f"SUMMARY: Applied: {len(self.applied)} | Incompatible/Skipped: {len(self.skipped)} | Errors: {len(self.failed)}",
            "============================================================",
            "",
        ]

        if not self.has_warnings:
            lines.append("PERFECT MATCH: All settings were applied cleanly without incompatibility.\n")
        else:
            if self.skipped:
                lines.append(f"--- INCOMPATIBLE / SKIPPED SETTINGS ({len(self.skipped)}) ---")
                lines.append("The following settings could not be assigned due to Blender version differences:")
                for item in self.skipped:
                    lines.append(f"  * [{item.category}] {item.label} ({item.field})")
                    lines.append(f"    Value in preset: {repr(item.value)}")
                    lines.append(f"    Reason: {item.reason}")
                lines.append("")

            if self.failed:
                lines.append(f"--- FAILED ASSIGNMENTS ({len(self.failed)}) ---")
                for item in self.failed:
                    lines.append(f"  * [{item.category}] {item.label} ({item.field})")
                    lines.append(f"    Value: {repr(item.value)}")
                    lines.append(f"    Error: {item.reason}")
                lines.append("")

        lines.append(f"--- APPLIED SETTINGS ({len(self.applied)}) ---")
        for item in self.applied:
            lines.append(f"  + [{item.category}] {item.label}: {repr(item.value)}")

        lines.append("\n======================= End of Report =======================")
        return "\n".join(lines)
