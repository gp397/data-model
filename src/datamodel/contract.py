from __future__ import annotations

from typing import Any, Dict
from jsonschema import Draft202012Validator


class ContractError(ValueError):
    pass


def build_contract_validator(contract: Dict[str, Any]) -> Draft202012Validator:
    try:
        return Draft202012Validator(contract)
    except Exception as exc:  # pragma: no cover - jsonschema throws many types
        raise ContractError(f"Invalid JSON schema contract: {exc}") from exc


def entity_schema(contract: Dict[str, Any], entity_name: str) -> Dict[str, Any]:
    defs = contract.get("$defs") or contract.get("definitions")
    if not isinstance(defs, dict) or entity_name not in defs:
        raise ContractError(f"Contract missing definition for '{entity_name}'")
    return defs[entity_name]
