from __future__ import annotations

from datamodel.contract import build_contract_validator
from datamodel.io import load_json, load_yaml, write_json
from datamodel.linker import LinkingError, link_entities
from datamodel.model_loader import load_model
from datamodel.pydantic_factory import build_models
from datamodel.validators import DataValidationError, validate_data


class PipelineError(RuntimeError):
    pass


def run_pipeline(model_path: str, data_path: str, contract_path: str, output_dir: str) -> dict:
    model = load_model(model_path)
    contract = load_json(contract_path)
    build_contract_validator(contract)
    data = load_yaml(data_path)

    pydantic_models = build_models(model)

    try:
        validated = validate_data(model, pydantic_models, contract, data)
        linked = link_entities(model, validated)
    except DataValidationError as exc:
        raise PipelineError(_format_issues("validation", exc.issues)) from exc
    except LinkingError as exc:
        raise PipelineError(_format_issues("linking", exc.issues)) from exc

    return {
        "model_version": model.version,
        "entities": linked,
    }


def write_outputs(output_dir: str, payload: dict) -> None:
    from pathlib import Path

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    data_path = Path(output_dir) / "validated_data.json"
    report_path = Path(output_dir) / "report.json"

    write_json(str(data_path), payload)
    report = {
        "entity_counts": {
            entity: len(items) for entity, items in payload["entities"].items()
        }
    }
    write_json(str(report_path), report)


def _format_issues(kind: str, issues: list) -> str:
    lines = [f"Pipeline failed during {kind} with {len(issues)} issue(s):"]
    for issue in issues[:20]:
        lines.append(f"- {issue.entity}[{issue.index}]: {issue.message}")
    if len(issues) > 20:
        lines.append(f"- ...and {len(issues) - 20} more")
    return "\n".join(lines)
