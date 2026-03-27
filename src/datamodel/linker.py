from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from datamodel.schema import EntitySpec, ModelSpec, RelationshipSpec


@dataclass
class LinkIssue:
    entity: str
    index: int
    message: str


class LinkingError(ValueError):
    def __init__(self, issues: List[LinkIssue]):
        super().__init__("Relationship linking failed")
        self.issues = issues


def link_entities(model: ModelSpec, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    entity_map = model.entity_map()
    issues: List[LinkIssue] = []

    lookup = _build_lookup(entity_map, data, issues)
    enriched: Dict[str, List[Dict[str, Any]]] = {}

    for entity_name, items in data.items():
        entity_spec = entity_map[entity_name]
        new_items: List[Dict[str, Any]] = []
        for idx, item in enumerate(items):
            enriched_item = dict(item)
            _apply_computed_fields(entity_spec, enriched_item, issues, idx)
            relationships = _resolve_relationships(entity_spec, enriched_item, lookup, issues, idx)
            enriched_item["relationships"] = relationships
            new_items.append(enriched_item)
        enriched[entity_name] = new_items

    if issues:
        raise LinkingError(issues)

    return enriched


def _build_lookup(
    entity_map: Dict[str, EntitySpec],
    data: Dict[str, List[Dict[str, Any]]],
    issues: List[LinkIssue],
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    lookup: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for entity_name, items in data.items():
        spec = entity_map[entity_name]
        entity_lookup: Dict[str, Dict[str, Any]] = {}
        for idx, item in enumerate(items):
            key = item.get(spec.id_field)
            if key is None:
                issues.append(LinkIssue(entity_name, idx, f"Missing id field '{spec.id_field}'"))
                continue
            if key in entity_lookup:
                issues.append(LinkIssue(entity_name, idx, f"Duplicate id '{key}'"))
                continue
            entity_lookup[key] = item
        lookup[entity_name] = entity_lookup

    return lookup


def _apply_computed_fields(
    entity: EntitySpec,
    item: Dict[str, Any],
    issues: List[LinkIssue],
    idx: int,
) -> None:
    for computed in entity.computed_fields:
        try:
            item[computed.name] = computed.template.format(**item)
        except KeyError as exc:
            issues.append(LinkIssue(entity.name, idx, f"Computed field missing key: {exc}"))


def _resolve_relationships(
    entity: EntitySpec,
    item: Dict[str, Any],
    lookup: Dict[str, Dict[str, Dict[str, Any]]],
    issues: List[LinkIssue],
    idx: int,
) -> Dict[str, Any]:
    resolved: Dict[str, Any] = {}

    for relationship in entity.relationships:
        value = item.get(relationship.name)
        if value is None:
            if relationship.required:
                issues.append(
                    LinkIssue(entity.name, idx, f"Missing required relationship '{relationship.name}'")
                )
            continue

        target_map = lookup.get(relationship.target, {})
        resolved_value = _resolve_value(relationship, value, target_map, issues, entity.name, idx)
        resolved[relationship.name] = resolved_value

    return resolved


def _resolve_value(
    relationship: RelationshipSpec,
    value: Any,
    target_map: Dict[str, Dict[str, Any]],
    issues: List[LinkIssue],
    entity_name: str,
    idx: int,
) -> Any:
    cardinality = relationship.cardinality
    if cardinality in {"many_to_one", "one_to_one"}:
        return _resolve_single(relationship, value, target_map, issues, entity_name, idx)

    if not isinstance(value, list):
        issues.append(LinkIssue(entity_name, idx, f"Relationship '{relationship.name}' must be a list"))
        return []

    resolved_list = []
    for item_id in value:
        resolved_list.append(
            _resolve_single(relationship, item_id, target_map, issues, entity_name, idx)
        )
    return resolved_list


def _resolve_single(
    relationship: RelationshipSpec,
    item_id: Any,
    target_map: Dict[str, Dict[str, Any]],
    issues: List[LinkIssue],
    entity_name: str,
    idx: int,
) -> Dict[str, Any]:
    if item_id not in target_map:
        issues.append(
            LinkIssue(entity_name, idx, f"Relationship '{relationship.name}' missing target '{item_id}'")
        )
        return {}

    target = target_map[item_id]
    if relationship.resolve_fields:
        return {field: target.get(field) for field in relationship.resolve_fields}

    return dict(target)
