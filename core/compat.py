"""RenderGate Version Compatibility Module.
Provides helper functions, known version differences, and guidance messages
when migrating presets between different Blender versions.
"""

from typing import Dict, Optional, Tuple
import bpy


# Known notable changes across Blender versions for render settings
KNOWN_MIGRATION_NOTES: Dict[str, str] = {
    "scene.eevee.use_bloom": (
        "In Blender 4.2+ (EEVEE Next), legacy Bloom was removed in favor of the "
        "Compositor Glare node."
    ),
    "scene.eevee.use_ssr": (
        "In Blender 4.2+ (EEVEE Next), Screen Space Reflections are replaced by "
        "Raytracing / Screen Tracing settings."
    ),
    "scene.eevee.use_gtao": (
        "In Blender 4.2+ (EEVEE Next), Ambient Occlusion is integrated into the Fast GI system."
    ),
    "scene.eevee.gi_diffuse_bounces": (
        "EEVEE Next Fast GI diffuse bounces setting."
    ),
    "scene.cycles.use_light_tree": (
        "Cycles Light Tree was introduced in Blender 3.5+."
    ),
    "scene.view_settings.view_transform": (
        "AgX color transform was introduced in Blender 4.0. Older versions use Filmic/Standard."
    ),
}


def get_current_blender_version() -> Tuple[int, int, int]:
    """Returns the current Blender version as a tuple (major, minor, patch)."""
    return bpy.app.version


def get_compatibility_hint(field_path: str, source_version_str: Optional[str] = None) -> Optional[str]:
    """Returns an explanatory hint if this property is a known cross-version change."""
    return KNOWN_MIGRATION_NOTES.get(field_path, None)


def parse_version_string(ver_str: str) -> Tuple[int, int, int]:
    """Parses a version string like '4.5.0' or '5.2.2 LTS' into (major, minor, patch)."""
    parts = []
    clean = ver_str.split()[0] if " " in ver_str else ver_str
    for segment in clean.split("."):
        try:
            parts.append(int(segment))
        except ValueError:
            break
    while len(parts) < 3:
        parts.append(0)
    return (parts[0], parts[1], parts[2])
