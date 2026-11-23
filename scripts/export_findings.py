#!/usr/bin/env python3
"""Export a new descriptive view from verified frozen records, outside this repository."""
import argparse
import json
from pathlib import Path
from verify_evidence import ROOT, records, verify, require, number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Refusing to overwrite an existing report")
    require(not args.output.resolve().is_relative_to(ROOT), "Write derived reports outside the frozen candidate")
    validation = verify(ROOT)
    require(validation["archived_verification"] == "PASS", "Archived-evidence checks did not pass")
    key = lambda r: (int(r["n"]), number(r["tau"]), number(r["kappa"]), r["estimator"])
    summaries = {}
    powers = {}
    for n in (500, 1000):
        for r in records(ROOT, f"results/main/n{n}/summary.csv"): summaries[key(r)] = r
        for r in records(ROOT, f"results/main/n{n}/power_summary.csv"):
            powers[key(r) + (number(r["Delta"]),)] = r
    k = (1000, .5, .1, "DML-IVQR-BC")
    dml_keys = [k for k in summaries if k[-1] == "DML-IVQR-BC"]
    wins = lambda e: sum(number(summaries[k]["RMSE"]) < number(summaries[k[:-1] + (e,)]["RMSE"])
                         for k in dml_keys)
    output = {
        "scope": "Descriptive view of archived reference-cutoff results, not new research results or calibrated inference",
        "source_manifest_sha256": validation["checks"][0]["detail"]["manifest_sha256"],
        "example_design": {"n": 1000, "tau": .5, "kappa": .1, "estimator": "DML-IVQR-BC"},
        "direct_truth_acceptance": number(summaries[k]["Coverage"]),
        "median_grid_quadrature": number(summaries[k]["median_grid_accepted_set_measure"]),
        "full_grid_acceptance_frequency": number(summaries[k]["all_41_acceptance_rate"]),
        "false_candidate_delta": .5,
        "false_candidate_rejection": number(powers[k + (.5,)]["power"]),
        "DML_lower_RMSE_than_Full": wins("Full-GMM"),
        "DML_lower_RMSE_than_Oracle": wins("Oracle-GMM"),
        "matched_designs": len(dml_keys),
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__": main()
