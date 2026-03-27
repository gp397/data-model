from __future__ import annotations

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field, create_model

from datamodel.schema import EntitySpec, FieldSpec, ModelSpec, RelationshipSpec


_TYPE_MAP: Dict[str, Any] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


class ModelBuildError(ValueError):
    pass


def build_models(model: ModelSpec) -> Dict[str, Type[BaseModel]]:
    models: Dict[str, Type[BaseModel]] = {}
    for entity in model.entities:
        models[entity.name] = _build_entity_model(entity)
    return models


def _build_entity_model(entity: EntitySpec) -> Type[BaseModel]:
    fields: Dict[str, Any] = {}

    for field in entity.fields:
        fields[field.name] = _build_field(field)

    for relationship in entity.relationships:
        fields[relationship.name] = _build_relationship_field(relationship)

    return create_model(entity.name, **fields)  # type: ignore[arg-type]


def _build_field(field: FieldSpec) -> Any:
    python_type = _TYPE_MAP.get(field.type)
    if python_type is None:
        raise ModelBuildError(f"Unknown field type '{field.type}'")

    if field.required:
        default = ...
        type_ = python_type
    else:
        default = None
        type_ = Optional[python_type]

    if field.regex:
        return (type_, Field(default, regex=field.regex, description=field.description))

    return (type_, Field(default, description=field.description))


def _build_relationship_field(relationship: RelationshipSpec) -> Any:
    cardinality = relationship.cardinality
    if cardinality in {"many_to_one", "one_to_one"}:
        relation_type = str
    elif cardinality in {"many_to_many", "one_to_many"}:
        relation_type = List[str]
    else:
        raise ModelBuildError(f"Unknown relationship cardinality '{cardinality}'")

    if relationship.required:
        default = ...
        type_ = relation_type
    else:
        default = None
        type_ = Optional[relation_type]

    return (type_, Field(default))
