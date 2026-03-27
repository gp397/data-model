from __future__ import annotations

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from datamodel.pipeline import run_pipeline
from datamodel.io import load_json, load_yaml
from datamodel.model_loader import load_model
from datamodel.pydantic_factory import build_models
from datamodel.validators import DataValidationError, validate_data
from datamodel.linker import LinkingError, link_entities


MODEL_PATH = ROOT / "demo" / "model" / "model.yaml"
DATA_PATH = ROOT / "demo" / "data" / "data.yaml"
CONTRACT_PATH = ROOT / "demo" / "contracts" / "api_contract.json"


def test_pipeline_success(tmp_path: Path) -> None:
    payload = run_pipeline(
        model_path=str(MODEL_PATH),
        data_path=str(DATA_PATH),
        contract_path=str(CONTRACT_PATH),
        output_dir=str(tmp_path),
    )
    assert payload["model_version"] == 1
    assert "Course" in payload["entities"]
    assert payload["entities"]["Course"][0]["relationships"]["teacher_id"]["id"] == "T-001"


def test_validation_rejects_bad_regex() -> None:
    model = load_model(str(MODEL_PATH))
    contract = load_json(str(CONTRACT_PATH))
    data = load_yaml(str(DATA_PATH))
    data["Teacher"][0]["id"] = "BAD-1"

    pydantic_models = build_models(model)
    with pytest.raises(DataValidationError):
        validate_data(model, pydantic_models, contract, data)


def test_linking_rejects_missing_reference() -> None:
    model = load_model(str(MODEL_PATH))
    contract = load_json(str(CONTRACT_PATH))
    data = load_yaml(str(DATA_PATH))
    data["Course"][0]["teacher_id"] = "T-999"

    pydantic_models = build_models(model)
    validated = validate_data(model, pydantic_models, contract, data)

    with pytest.raises(LinkingError):
        link_entities(model, validated)
