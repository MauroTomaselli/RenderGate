"""RenderGate Serializer.
Extracts Blender scene render settings and serializes them into a structured,
self-documenting format with field paths, human-readable labels, descriptions, and types.
"""

from typing import Dict, Any, List, Optional
import bpy


def _serialize_value(val: Any) -> Any:
    """Converts Blender RNA values to pure JSON-serializable Python primitives."""
    if hasattr(val, "__len__") and not isinstance(val, (str, bytes)):
        return [_serialize_value(item) for item in val]
    return val


def _extract_rna_property(target_obj: Any, prop_name: str, field_path: str) -> Optional[Dict[str, Any]]:
    """Inspects a single Blender RNA property and returns its serialized dictionary representation."""
    if not hasattr(target_obj, "bl_rna"):
        return None
    prop_rna = target_obj.bl_rna.properties.get(prop_name)
    if not prop_rna or prop_rna.is_readonly:
        return None
    if prop_rna.type in ("POINTER", "COLLECTION"):
        return None

    try:
        val = getattr(target_obj, prop_name)
        return {
            "field": field_path,
            "label": prop_rna.name,
            "description": prop_rna.description or prop_rna.name,
            "type": prop_rna.type,
            "value": _serialize_value(val),
        }
    except Exception:
        return None


def serialize_object_properties(
    target_obj: Any,
    field_prefix: str,
    include_props: Optional[List[str]] = None,
    exclude_props: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Iterates through an object's RNA properties and serializes them."""
    if not target_obj or not hasattr(target_obj, "bl_rna"):
        return []

    results = []
    exclude_set = set(exclude_props or [])
    exclude_set.update({"rna_type", "name"})

    prop_keys = include_props if include_props is not None else target_obj.bl_rna.properties.keys()

    for key in prop_keys:
        if key in exclude_set:
            continue
        field_path = f"{field_prefix}.{key}"
        entry = _extract_rna_property(target_obj, key, field_path)
        if entry is not None:
            results.append(entry)

    return results


class SceneSerializer:
    """Serializes all scene render settings into a complete RenderGate dictionary."""

    def __init__(self, scene: bpy.types.Scene, view_layer: Optional[bpy.types.ViewLayer] = None):
        self.scene = scene
        self.view_layer = view_layer or getattr(bpy.context, "view_layer", None) or scene.view_layers[0]

    def serialize_dimensions(self) -> Dict[str, Any]:
        """Dimensions, aspect ratio, frame rate, and border settings."""
        props = [
            "resolution_x",
            "resolution_y",
            "resolution_percentage",
            "pixel_aspect_x",
            "pixel_aspect_y",
            "fps",
            "fps_base",
            "frame_start",
            "frame_end",
            "frame_step",
            "use_border",
            "use_crop_to_border",
        ]
        return {
            "category_label": "Dimensions & Framing",
            "category_id": "dimensions",
            "properties": serialize_object_properties(self.scene.render, "scene.render", include_props=props),
        }

    def serialize_engine_general(self) -> Dict[str, Any]:
        """Engine selection, film transparency, dither, and simplify."""
        render_props = [
            "engine",
            "film_transparent",
            "dither_intensity",
            "use_simplify",
            "simplify_subdivision",
            "simplify_child_particles",
        ]
        props_list = serialize_object_properties(self.scene.render, "scene.render", include_props=render_props)
        return {
            "category_label": "Render Engine & General",
            "category_id": "engine",
            "properties": props_list,
        }

    def serialize_color_management(self) -> Dict[str, Any]:
        """View transform (AgX/Filmic/Standard), look, exposure, gamma, and display device."""
        props_view = serialize_object_properties(
            self.scene.view_settings,
            "scene.view_settings",
            include_props=["view_transform", "look", "exposure", "gamma", "use_curve_mapping"],
        )
        props_display = serialize_object_properties(
            self.scene.display_settings,
            "scene.display_settings",
            include_props=["display_device"],
        )
        return {
            "category_label": "Color Management",
            "category_id": "color_management",
            "properties": props_view + props_display,
        }

    def serialize_cycles(self) -> Dict[str, Any]:
        """All Cycles engine properties (samples, bounces, denoising, light tree, etc.)."""
        if not hasattr(self.scene, "cycles"):
            return {"category_label": "Cycles Engine Settings", "category_id": "cycles", "properties": []}

        # Exclude internal non-render properties or datablock links
        excludes = [
            "shading_system",
            "preview_pause",
        ]
        props_list = serialize_object_properties(self.scene.cycles, "scene.cycles", exclude_props=excludes)
        return {
            "category_label": "Cycles Engine Settings",
            "category_id": "cycles",
            "properties": props_list,
        }

    def serialize_eevee(self) -> Dict[str, Any]:
        """All EEVEE / EEVEE Next engine properties."""
        if not hasattr(self.scene, "eevee"):
            return {"category_label": "EEVEE Engine Settings", "category_id": "eevee", "properties": []}

        props_list = serialize_object_properties(self.scene.eevee, "scene.eevee")
        return {
            "category_label": "EEVEE Engine Settings",
            "category_id": "eevee",
            "properties": props_list,
        }

    def serialize_output_format(self) -> Dict[str, Any]:
        """File format, color mode, compression, quality, etc."""
        image_settings_props = [
            "file_format",
            "color_mode",
            "color_depth",
            "quality",
            "compression",
            "exr_codec",
            "tiff_codec",
        ]
        props_list = serialize_object_properties(
            self.scene.render.image_settings,
            "scene.render.image_settings",
            include_props=image_settings_props,
        )
        return {
            "category_label": "Output Format & Compression",
            "category_id": "output_format",
            "properties": props_list,
        }

    def serialize_passes(self) -> Dict[str, Any]:
        """Active View Layer render passes (Z, Mist, Normal, Cryptomatte, AO, etc.)."""
        props_list = []
        if self.view_layer:
            # Standard view layer passes
            for key in self.view_layer.bl_rna.properties.keys():
                if key.startswith("use_pass_"):
                    entry = _extract_rna_property(self.view_layer, key, f"view_layer.{key}")
                    if entry:
                        props_list.append(entry)

            # Cycles-specific view layer passes if available
            if hasattr(self.view_layer, "cycles"):
                for key in self.view_layer.cycles.bl_rna.properties.keys():
                    if key.startswith("use_pass_") or key.startswith("denoising_"):
                        entry = _extract_rna_property(self.view_layer.cycles, key, f"view_layer.cycles.{key}")
                        if entry:
                            props_list.append(entry)

        return {
            "category_label": "View Layer Passes",
            "category_id": "passes",
            "properties": props_list,
        }

    def serialize_all(
        self,
        preset_name: str = "Untitled Preset",
        description: str = "",
        categories: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Builds the full serializable dictionary for a .RGE preset file."""
        import datetime

        categories_filter = set(categories) if categories else None

        all_categories = {
            "dimensions": self.serialize_dimensions,
            "engine": self.serialize_engine_general,
            "color_management": self.serialize_color_management,
            "cycles": self.serialize_cycles,
            "eevee": self.serialize_eevee,
            "output_format": self.serialize_output_format,
            "passes": self.serialize_passes,
        }

        selected_categories = {}
        for cat_id, cat_func in all_categories.items():
            if categories_filter is None or cat_id in categories_filter:
                selected_categories[cat_id] = cat_func()

        meta = {
            "addon": "RenderGate",
            "addon_version": "1.0.0",
            "format_version": "1.0",
            "blender_version": list(bpy.app.version),
            "blender_version_str": bpy.app.version_string,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "preset_name": preset_name,
            "description": description,
        }

        return {
            "_rendergate_meta": meta,
            "categories": selected_categories,
        }
