For Wayne...

This is the first commit of some semi working example scripts, there is much to do!

The overall aim is to demonstrate:
- Loading a dynamic class model from yaml into RAM
  - Class model must be able to version classes with different attributes on different versions
  - Class model must be able to define relationships and if they are mandatory or not
- Export visual representation of that model
- Load data into the model and vallidate correctness of data, mandatory relationships must exist, invalid objects (lacking mandatory atributes) fail to import etc.
- Visualise the loaded data
- Store imported data in DB (sqlite for example) with a version/date so that each successive run/import can produce a diff from the current "baseline"

## TODO

Everything

## Working Demo (Runtime Model + Contract Validation)

This demo builds a dynamic data model from YAML, validates data against a JSON Schema API contract, links relationships by ID, enriches with computed fields, and emits validated output.

### Files

- `demo/model/model.yaml`: model definition (fields, regex, relationships, computed fields)
- `demo/contracts/api_contract.json`: API contract JSON Schema
- `demo/data/data.yaml`: sample data
- `src/datamodel/cli.py`: CLI runner

### Run

```bash
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m datamodel.cli \
  --model demo/model/model.yaml \
  --data demo/data/data.yaml \
  --contract demo/contracts/api_contract.json \
  --output output/demo_run
```

Outputs:
- `output/demo_run/validated_data.json`
- `output/demo_run/report.json`
