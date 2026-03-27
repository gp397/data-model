from __future__ import annotations

import argparse
import sys

from datamodel.pipeline import PipelineError, run_pipeline, write_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the dynamic data model demo pipeline")
    parser.add_argument("--model", required=True, help="Path to model YAML")
    parser.add_argument("--data", required=True, help="Path to data YAML")
    parser.add_argument("--contract", required=True, help="Path to API contract JSON")
    parser.add_argument("--output", required=True, help="Output directory")

    args = parser.parse_args()

    try:
        payload = run_pipeline(
            model_path=args.model,
            data_path=args.data,
            contract_path=args.contract,
            output_dir=args.output,
        )
    except PipelineError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    write_outputs(args.output, payload)
    print(f"Validated data written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
