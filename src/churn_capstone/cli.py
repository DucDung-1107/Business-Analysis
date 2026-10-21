"""Independent team stages; all paths are relative to the current working directory."""
import argparse
import json
from pathlib import Path

from . import analysis, classification, data, features, monitoring, segmentation
from .contracts import CONTRACT_VERSION, Customer, FeatureRow, MonthlyBehavior, SegmentProfile, read_table
from .integration import load_runtime, predict, write_json


def run_stage(stage, directory, config):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if config.get("mode") != "demo" or config.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("Demo command requires a compatible explicit demo config")
    if stage == "data":
        customers, behavior = data.generate_demo(config["seed"], config["n_customers"])
        customers.to_csv(directory / "customers.csv", index=False)
        behavior.to_csv(directory / "monthly_behavior.csv", index=False)
        write_json(directory / "data_quality.json", data.validate_inputs(customers, behavior))
        write_json(directory / "provenance.json", {**config, "source": "generated-demo-fixture"})
        return
    if stage == "features":
        customers = read_table(directory / "customers.csv", Customer)
        behavior = read_table(directory / "monthly_behavior.csv", MonthlyBehavior)
        frame = features.build_features(customers, behavior, config["as_of_date"],
                                        config["observation_months"])
        frame.to_csv(directory / "features.csv", index=False)
        # This demo snapshots its fixture as a drift reference, never production training data.
        frame.to_csv(directory / "reference_features.csv", index=False)
        return
    frame = read_table(directory / "features.csv", FeatureRow)
    if stage == "eda":
        summary = analysis.summarize(frame, read_table(directory / "customers.csv", Customer),
                                     read_table(directory / "monthly_behavior.csv", MonthlyBehavior))
        write_json(directory / "eda_summary.json", summary)
        return
    if stage == "classifier":
        write_json(directory / "classifier.json", classification.build_bundle(frame))
        write_json(directory / "classifier_metrics.json", {
            "mode": "demo", "status": "not_trained", "metrics": None,
            "required_real_metrics": ["roc_auc", "precision", "recall", "f1"],
        })
        return
    if stage == "segmentation":
        write_json(directory / "segmenter.json", segmentation.build_bundle(frame))
        assignments = segmentation.DemoSegmenter().assign_segments(frame)
        profiles = segmentation.describe_segments(assignments)
        profiles.to_csv(directory / "segment_profiles.csv", index=False)
        write_json(directory / "segmentation_metrics.json", {
            "mode": "demo", "status": "rule_fixture", "silhouette": None,
        })
        return
    if stage == "predict":
        classifier, segmenter, versions = load_runtime(directory)
        profiles = read_table(directory / "segment_profiles.csv", SegmentProfile)
        results = predict(frame, classifier, segmenter, profiles)
        results.to_csv(directory / "predictions.csv", index=False)
        write_json(directory / "prediction_metadata.json", {
            "mode": "demo", "contract_version": CONTRACT_VERSION, "model_versions": versions,
        })
        return
    if stage == "monitor":
        import pandas as pd
        report = monitoring.drift_report(
            read_table(directory / "reference_features.csv", FeatureRow), frame,
            config["psi_threshold"],
        )
        report.update(mode="demo", performance=monitoring.performance_report(
            pd.read_csv(directory / "predictions.csv", dtype={"customer_id": "string"})
        ))
        write_json(directory / "monitoring.json", report)
        return
    raise ValueError(f"Unknown stage: {stage}")


STAGES = ("data", "features", "eda", "classifier", "segmentation", "predict", "monitor")


def main():
    parser = argparse.ArgumentParser(description="DEMO ONLY: team integration pipeline")
    parser.add_argument("stage", choices=("demo",) + STAGES)
    parser.add_argument("--output", default="artifacts/demo")
    parser.add_argument("--config", default="configs/demo.json")
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        for stage in STAGES if args.stage == "demo" else [args.stage]:
            run_stage(stage, args.output, config)
            print(f"[demo] {stage}: passed")
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"Pipeline failed: {error}\n")


if __name__ == "__main__":
    main()
