from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from jsonschema import Draft202012Validator
from pydantic import BaseModel, ValidationError as PydanticError

from datamodel.contract import entity_schema
from datamodel.schema import ModelSpec


@dataclass
class ValidationIssue:
    entity: str
    index: int
    message: str


class DataValidationError(ValueError):
    def __init__(self, issues: List[ValidationIssue]):
        super().__init__("Data validation failed")
        self.issues = issues


def validate_data(
    model: ModelSpec,
    pydantic_models: Dict[str, type[BaseModel]],
    contract: Dict[str, Any],
    data: Dict[str, Any],
) -> Dict[str, List[Dict[str, Any]]]:
    issues: List[ValidationIssue] = []
    validated: Dict[str, List[Dict[str, Any]]] = {}

    entity_map = model.entity_map()

    for entity_name, items in data.items():
        if entity_name not in entity_map:
            issues.append(ValidationIssue(entity_name, -1, "Entity not in model"))
            continue

        if not isinstance(items, list):
            issues.append(ValidationIssue(entity_name, -1, "Entity data must be a list"))
            continue

        schema = entity_schema(contract, entity_name)
        schema_validator = Draft202012Validator(schema)
        pyd_model = pydantic_models[entity_name]

        validated_items: List[Dict[str, Any]] = []
        for idx, item in enumerate(items):
            for error in schema_validator.iter_errors(item):
                issues.append(ValidationIssue(entity_name, idx, f"Contract: {error.message}"))

            try:
                validated_item = pyd_model.parse_obj(item).dict()
                validated_items.append(validated_item)
            except PydanticError as exc:
                for err in exc.errors():
                    msg = f"Model: {err['loc']}: {err['msg']}"
                    issues.append(ValidationIssue(entity_name, idx, msg))

        validated[entity_name] = validated_items

    if issues:
        raise DataValidationError(issues)

    return validated
