from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class FieldSpec:
    name: str
    type: str
    required: bool = False
    regex: Optional[str] = None
    description: Optional[str] = None


@dataclass(frozen=True)
class RelationshipSpec:
    name: str
    target: str
    cardinality: str
    required: bool = False
    resolve_fields: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ComputedFieldSpec:
    name: str
    template: str


@dataclass(frozen=True)
class EntitySpec:
    name: str
    id_field: str
    fields: List[FieldSpec]
    relationships: List[RelationshipSpec] = field(default_factory=list)
    computed_fields: List[ComputedFieldSpec] = field(default_factory=list)


@dataclass(frozen=True)
class ModelSpec:
    version: int
    entities: List[EntitySpec]

    def entity_map(self) -> dict[str, EntitySpec]:
        return {entity.name: entity for entity in self.entities}
