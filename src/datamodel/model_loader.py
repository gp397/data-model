from __future__ import annotations

from typing import Any, Dict, List
import yaml

from datamodel.schema import (
    ComputedFieldSpec,
    EntitySpec,
    FieldSpec,
    ModelSpec,
    RelationshipSpec,
)


class ModelSpecError(ValueError):
    pass


def load_model(path: str) -> ModelSpec:
    with open(path, "r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    if not isinstance(raw, dict):
        raise ModelSpecError("Model file must be a mapping")

    version = int(raw.get("version", 1))
    entities_raw = raw.get("entities")
    if not isinstance(entities_raw, dict):
        raise ModelSpecError("Model must define 'entities' as a mapping")

    entities: List[EntitySpec] = []
    for entity_name, entity_data in entities_raw.items():
        entities.append(_parse_entity(entity_name, entity_data))

    return ModelSpec(version=version, entities=entities)


def _parse_entity(entity_name: str, data: Dict[str, Any]) -> EntitySpec:
    if not isinstance(data, dict):
        raise ModelSpecError(f"Entity '{entity_name}' must be a mapping")

    id_field = data.get("id_field", "id")
    fields_raw = data.get("fields", [])
    if not isinstance(fields_raw, list):
        raise ModelSpecError(f"Entity '{entity_name}' fields must be a list")

    fields = [_parse_field(entity_name, item) for item in fields_raw]

    relationships_raw = data.get("relationships", [])
    relationships = [_parse_relationship(entity_name, item) for item in relationships_raw]

    computed_raw = data.get("computed_fields", [])
    computed_fields = [_parse_computed(entity_name, item) for item in computed_raw]

    return EntitySpec(
        name=entity_name,
        id_field=id_field,
        fields=fields,
        relationships=relationships,
        computed_fields=computed_fields,
    )


def _parse_field(entity_name: str, data: Dict[str, Any]) -> FieldSpec:
    if not isinstance(data, dict):
        raise ModelSpecError(f"Field in '{entity_name}' must be a mapping")

    name = data.get("name")
    type_ = data.get("type")
    if not name or not type_:
        raise ModelSpecError(f"Field in '{entity_name}' requires name and type")

    return FieldSpec(
        name=str(name),
        type=str(type_),
        required=bool(data.get("required", False)),
        regex=data.get("regex"),
        description=data.get("description"),
    )


def _parse_relationship(entity_name: str, data: Dict[str, Any]) -> RelationshipSpec:
    if not isinstance(data, dict):
        raise ModelSpecError(f"Relationship in '{entity_name}' must be a mapping")

    name = data.get("name")
    target = data.get("target")
    cardinality = data.get("cardinality")
    if not name or not target or not cardinality:
        raise ModelSpecError(
            f"Relationship in '{entity_name}' requires name, target, cardinality"
        )

    resolve_fields = data.get("resolve_fields", [])
    if resolve_fields is None:
        resolve_fields = []

    return RelationshipSpec(
        name=str(name),
        target=str(target),
        cardinality=str(cardinality),
        required=bool(data.get("required", False)),
        resolve_fields=[str(field) for field in resolve_fields],
    )


def _parse_computed(entity_name: str, data: Dict[str, Any]) -> ComputedFieldSpec:
    if not isinstance(data, dict):
        raise ModelSpecError(f"Computed field in '{entity_name}' must be a mapping")

    name = data.get("name")
    template = data.get("template")
    if not name or not template:
        raise ModelSpecError(f"Computed field in '{entity_name}' requires name and template")

    return ComputedFieldSpec(name=str(name), template=str(template))
