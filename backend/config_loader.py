"""Media configuration loader for Watch1 backend."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "watch_media_dirs.yml"


class ConfigError(RuntimeError):
    """Raised when media configuration cannot be parsed or validated."""


@dataclass(frozen=True)
class MediaCategory:
    key: str
    label: str
    media_type: str
    storage_format: str
    root_path: str
    default: bool = False
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    hierarchy_levels: List[str] = field(default_factory=list)
    playback: Dict[str, Any] = field(default_factory=dict)
    ui: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MediaCatalogConfig:
    version: int
    categories: List[MediaCategory]
    defaults: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)

    def get_category(self, key: str) -> MediaCategory:
        for category in self.categories:
            if category.key == key:
                return category
        raise KeyError(f"Media category '{key}' is not defined in configuration")

    @property
    def default_category(self) -> Optional[MediaCategory]:
        for category in self.categories:
            if category.default:
                return category
        return self.categories[0] if self.categories else None


_cached_config: Optional[MediaCatalogConfig] = None
_cached_path: Optional[Path] = None


def load_media_config(path: Optional[Path | str] = None, *, force: bool = False) -> MediaCatalogConfig:
    """Load and cache the media catalog configuration."""
    global _cached_config, _cached_path

    config_path = _resolve_path(path)

    if not force and _cached_config is not None and config_path == _cached_path:
        return _cached_config

    data = _read_yaml(config_path)
    config = _parse_config(data, config_path)

    _cached_config = config
    _cached_path = config_path
    return config


def reload_media_config(path: Optional[Path | str] = None) -> MediaCatalogConfig:
    """Force reload the configuration regardless of cache state."""
    return load_media_config(path, force=True)


def _resolve_path(path: Optional[Path | str]) -> Path:
    if path is None:
        return DEFAULT_CONFIG_PATH
    path_obj = Path(path)
    if not path_obj.is_absolute():
        path_obj = (PROJECT_ROOT / path_obj).resolve()
    return path_obj


def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Media configuration file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as stream:
            data = yaml.safe_load(stream) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Failed to parse YAML configuration at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError("Top-level media configuration must be a mapping")
    return data


def _parse_config(data: Dict[str, Any], path: Path) -> MediaCatalogConfig:
    version = data.get("version")
    if not isinstance(version, int):
        raise ConfigError("Configuration must define an integer 'version'")

    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ConfigError("'defaults' must be a mapping if provided")

    validation = data.get("validation", {})
    if not isinstance(validation, dict):
        raise ConfigError("'validation' must be a mapping if provided")

    categories_data = data.get("categories")
    if not isinstance(categories_data, list) or not categories_data:
        raise ConfigError("Configuration must include a non-empty 'categories' list")

    categories = [_build_category(entry, defaults, path) for entry in categories_data]

    _ensure_unique_keys(categories)
    _ensure_single_default(categories, strict=validation.get("strict", False))

    return MediaCatalogConfig(
        version=version,
        categories=categories,
        defaults=defaults,
        validation=validation,
    )


def _build_category(entry: Dict[str, Any], defaults: Dict[str, Any], path: Path) -> MediaCategory:
    if not isinstance(entry, dict):
        raise ConfigError("Each category must be a mapping")

    required_fields = ("key", "label", "root_path")
    for field_name in required_fields:
        if not entry.get(field_name):
            raise ConfigError(f"Category missing required field '{field_name}' in {path}")

    media_type = entry.get("media_type", defaults.get("media_type"))
    storage_format = entry.get("storage_format", defaults.get("storage_format"))
    include_patterns = entry.get("include_patterns", defaults.get("include_patterns", []))
    exclude_patterns = entry.get("exclude_patterns", defaults.get("exclude_patterns", []))

    if media_type not in {"video", "audio", "image"}:
        raise ConfigError(
            f"Category '{entry['key']}' defines invalid media_type '{media_type}'. "
            "Expected one of: video, audio, image"
        )
    if storage_format not in {"collection", "series", "group", "item"}:
        raise ConfigError(
            f"Category '{entry['key']}' defines invalid storage_format '{storage_format}'. "
            "Expected one of: collection, series, group, item"
        )

    hierarchy_levels: List[str] = []
    hierarchy = entry.get("hierarchy", {})
    if hierarchy:
        levels = hierarchy.get("levels", [])
        if not isinstance(levels, Iterable):
            raise ConfigError(
                f"Category '{entry['key']}' hierarchy levels must be a list"
            )
        for level in levels:
            if not isinstance(level, dict) or not level.get("name"):
                raise ConfigError(
                    f"Category '{entry['key']}' hierarchy entries must include a 'name'"
                )
            hierarchy_levels.append(level["name"])

    return MediaCategory(
        key=entry["key"],
        label=entry["label"],
        media_type=media_type,
        storage_format=storage_format,
        root_path=entry["root_path"],
        default=bool(entry.get("default", False)),
        include_patterns=list(include_patterns),
        exclude_patterns=list(exclude_patterns),
        hierarchy_levels=hierarchy_levels,
        playback=entry.get("playback", {}),
        ui=entry.get("ui", {}),
    )


def _ensure_unique_keys(categories: Iterable[MediaCategory]) -> None:
    seen: Dict[str, MediaCategory] = {}
    for category in categories:
        if category.key in seen:
            raise ConfigError(f"Duplicate media category key '{category.key}' detected")
        seen[category.key] = category


def _ensure_single_default(categories: Iterable[MediaCategory], *, strict: bool) -> None:
    defaults = [category for category in categories if category.default]
    if strict:
        if len(defaults) != 1:
            raise ConfigError(
                "Configuration validation requires exactly one default category"
            )
    elif len(defaults) > 1:
        raise ConfigError("Only one category may be marked as default")
