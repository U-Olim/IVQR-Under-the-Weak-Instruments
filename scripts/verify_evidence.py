#!/usr/bin/env python3
"""Read-only archived-evidence verification. Never imports historical code or R."""
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
ESTIMATORS = ("Oracle-GMM", "Full-GMM", "DML-IVQR-BC")
TAUS = (.1, .25, .5, .75, .9)
KAPPAS = (1., .5, .25, .1)
DELTAS = (-1., -.5, -.25, .25, .5, 1.)
CUTOFF = 5.99146454710798  # Historical recorded R cutoff, not recalibrated.
TOL = 2e-10


class MissingEvidence(Exception):
    pass


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(x):
    v = float(x)
    require(math.isfinite(v), f"Nonfinite number: {x}")
    return v


def flag(x):
    require(x in ("TRUE", "FALSE"), f"Invalid Boolean: {x}")
    return x == "TRUE"


def close(a, b, label="value", tolerance=TOL):
    require(abs(number(a) - number(b)) <= tolerance, f"{label}: {a} != {b}")


def cell(row):
    return (int(row["n"]), number(row["tau"]), number(row["kappa"]), row["estimator"])


def identity(row):
    return cell(row) + (int(row["replication"]),)


def records(root, relative):
    p = root / relative
    if not p.is_file():
        raise MissingEvidence(relative)
    opener = gzip.open if p.suffix == ".gz" else open
    with opener(p, "rt", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        require(reader.fieldnames is not None, f"Missing CSV header: {relative}")
        for row in reader:
            require(None not in row and None not in row.values(), f"Malformed CSV: {relative}")
            yield row


def digest(path, decompressed=False):
    h = hashlib.sha256()
    opener = gzip.open if decompressed else open
    with opener(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def safe_member(root, name):
    p = Path(name)
    require(not p.is_absolute() and ".." not in p.parts and "\\" not in name,
            f"Unsafe manifest path: {name}")
    resolved = (root / p).resolve()
    require(resolved.is_relative_to(root.resolve()), f"Manifest escape: {name}")
    require(not (root / p).is_symlink(), f"Symlink not supported: {name}")
    return resolved


def integrity(root):
    rows = list(records(root, "RELEASE_MANIFEST.csv"))
    require(rows, "Empty release manifest")
    listed = set()
    copied = compressed = 0
    for row in rows:
        name = row["release_path"]
        require(name not in listed, f"Duplicate manifest path: {name}")
        listed.add(name)
        p = safe_member(root, name)
        if not p.is_file():
            raise MissingEvidence(name)
        require(p.stat().st_size == int(row["release_bytes"]), f"Size mismatch: {name}")
        require(digest(p) == row["release_sha256"], f"SHA256 mismatch: {name}")
        if row["transformation"] == "gzip lossless mtime=0":
            require(digest(p, True) == row["source_sha256"], f"Decompressed SHA256: {name}")
            compressed += 1
        elif row["transformation"].startswith("byte-identical"):
            require(row["source_sha256"] == row["release_sha256"], f"Source identity: {name}")
            copied += 1
    payload = [p for p in root.rglob("*") if p.relative_to(root).parts[0] != ".git"]
    require(not any(p.is_symlink() for p in payload), "Symlinks are not supported in the frozen payload")
    actual = {p.relative_to(root).as_posix() for p in payload if p.is_file()}
    require(actual == listed | {"RELEASE_MANIFEST.csv"},
            f"Manifest inventory differs: {sorted(actual ^ (listed | {'RELEASE_MANIFEST.csv'}))[:20]}")
    return {"files": len(rows), "byte_identical_copies": copied,
            "lossless_compressed_archives": compressed,
            "manifest_sha256": digest(root / "RELEASE_MANIFEST.csv")}


def main_records(root):
    data, groups = {}, {}
    for n in (500, 1000):
        for row in records(root, f"results/main/n{n}/results.csv.gz"):
            key = identity(row)
            require(key not in data, f"Duplicate estimator record: {key}")
            require(key[0] == n and 1 <= key[-1] <= 500, f"Invalid identity: {key}")
            for name in ("failed", "coverage_failed", "profile_failed"):
                require(not flag(row[name]), f"Archived main failure: {key}/{name}")
            truth, point, w = map(number, (row["alpha_true"], row["alpha_hat"], row["W_true"]))
            close(truth, 1 + statistics.NormalDist().inv_cdf(key[1]), "structural truth")
            require(w >= 0, "Negative W")
            require(flag(row["covered"]) == (w <= CUTOFF), f"Truth decision: {key}")
            require(flag(row["rejected_true"]) == (w > CUTOFF), f"Truth rejection: {key}")
            for name, value in (("bias", truth-point), ("signed_error", point-truth),
                                ("absolute_error", abs(point-truth)), ("squared_error", (point-truth)**2)):
                close(row[name], value, f"{key}/{name}")
            data[key] = row
            groups.setdefault(key[:-1], []).append(row)
        require(not list(records(root, f"results/main/n{n}/failures.csv")), "Nonempty main failure ledger")
    expected = set(itertools.product((500, 1000), TAUS, KAPPAS, ESTIMATORS))
    require(set(groups) == expected, "Incorrect main design cells")
    for k, g in groups.items():
        require({int(x["replication"]) for x in g} == set(range(1, 501)) and len(g) == 500,
                f"Missing/duplicate replications: {k}")
    require(len(data) == 60000, "Expected 60,000 estimator records")
    return data, groups


def summaries(root, groups):
    saved = {}
    for n in (500, 1000):
        for row in records(root, f"results/main/n{n}/summary.csv"):
            k = cell(row)
            require(k not in saved and k in groups, f"Duplicate/unknown summary: {k}")
            saved[k] = row
            g = groups[k]
            means = {"Bias": "bias", "MAE": "absolute_error", "Coverage": "covered", "Size": "rejected_true",
                     "mean_grid_accepted_set_measure": "grid_accepted_set_measure",
                     "mean_accepted_grid_share": "accepted_grid_share",
                     "mean_number_accepted_grid_points": "number_accepted_grid_points",
                     "left_boundary_acceptance_rate": "left_boundary_accepted",
                     "right_boundary_acceptance_rate": "right_boundary_accepted",
                     "either_boundary_acceptance_rate": "either_boundary_accepted",
                     "both_boundaries_acceptance_rate": "both_boundaries_accepted",
                     "all_41_acceptance_rate": "all_41_grid_points_accepted"}
            val = lambda v: float(flag(v)) if v in ("TRUE", "FALSE") else number(v)
            for target, source in means.items():
                close(row[target], statistics.mean(val(r[source]) for r in g), f"{k}/{target}")
            close(row["RMSE"], math.sqrt(statistics.mean(number(r["squared_error"]) for r in g)), "RMSE")
            for target, source in (("median_grid_accepted_set_measure", "grid_accepted_set_measure"),
                                   ("median_accepted_grid_share", "accepted_grid_share")):
                close(row[target], statistics.median(number(r[source]) for r in g), target)
            for f in ("total_replications", "successful_profiles", "successful_coverage_evaluations"):
                close(row[f], 500, f)
            for f in ("failed_profiles", "failed_coverage_evaluations", "numerical_failures"):
                close(row[f], 0, f)
    require(set(saved) == set(groups), "Missing summaries")
    return saved


def power(root, data):
    count, groups, ids = 0, {}, set()
    for n in (500, 1000):
        for row in records(root, f"results/main/n{n}/power.csv.gz"):
            key, delta = identity(row), number(row["Delta"])
            require(key in data and key[0] == n and delta in DELTAS, "Unknown power design")
            ident = key + (delta,)
            require(ident not in ids, "Duplicate false-candidate record")
            ids.add(ident)
            require(not flag(row["power_evaluation_failed"]), "Archived false-candidate failure")
            close(row["a_false"], number(data[key]["alpha_true"]) + delta, "False candidate")
            w = number(row["W_false"])
            require(w >= 0, "Negative W")
            rejected = w > CUTOFF
            require(flag(row["rejected_false"]) == rejected and flag(row["rejection"]) == rejected,
                    "False-candidate rejection mismatch")
            close(row["false_acceptance"], 1-int(rejected), "False acceptance")
            groups.setdefault(key[:-1] + (delta,), []).append(rejected)
            count += 1
    require(count == 360000, "Expected 360,000 false-candidate records")
    summary_keys = set()
    for n in (500, 1000):
        for row in records(root, f"results/main/n{n}/power_summary.csv"):
            k = cell(row) + (number(row["Delta"]),)
            require(k in groups and k not in summary_keys, "Unknown/duplicate power summary")
            summary_keys.add(k)
            require(len(groups[k]) == 500, "Incomplete false-candidate cell")
            close(row["power"], statistics.mean(groups[k]), "Power summary")
            close(row["false_acceptance"], 1-statistics.mean(groups[k]), "False-acceptance summary")
            for f in ("total_replications", "successful_power_evaluations"):
                close(row[f], 500, f)
            for f in ("failed_power_evaluations", "numerical_failures"):
                close(row[f], 0, f)
    require(summary_keys == set(groups) and len(groups) == 720, "Power summary coverage")
    return {"rows": count, "cells": len(groups)}


def profiles(root, data):
    seen, total = set(), 0
    for n in (500, 1000):
        for key, iterator in itertools.groupby(records(root, f"results/main/n{n}/profiles.csv.gz"), identity):
            require(key not in seen and key in data and key[0] == n, "Duplicate/unknown grid profile")
            seen.add(key)
            rows = list(iterator)
            require(len(rows) == 41, "Expected 41 candidates per profile")
            w, accepted = [], []
            for j, row in enumerate(rows):
                close(row["a"], -1+j*.1, "Ordered candidate grid")
                v = number(row["W"])
                require(v >= 0, "Negative grid W")
                require(flag(row["accepted"]) == (v <= CUTOFF), "Grid acceptance mismatch")
                w.append(v)
                accepted.append(v <= CUTOFF)
            r = data[key]
            close(r["alpha_hat"], number(rows[min(range(41), key=lambda i: w[i])]["a"]), "First grid minimum")
            close(r["grid_accepted_set_measure"], sum(.05*(accepted[j]+accepted[j+1]) for j in range(40)), "Quadrature")
            close(r["number_accepted_grid_points"], sum(accepted), "Accepted count")
            close(r["accepted_grid_share"], sum(accepted)/41., "Accepted share")
            for f, v in (("left_boundary_accepted", accepted[0]), ("right_boundary_accepted", accepted[-1]),
                         ("either_boundary_accepted", accepted[0] or accepted[-1]),
                         ("both_boundaries_accepted", accepted[0] and accepted[-1]),
                         ("all_41_grid_points_accepted", all(accepted))):
                require(flag(r[f]) == v, f"Profile diagnostic: {f}")
            total += len(rows)
    require(seen == set(data) and total == 2460000, "Expected 2,460,000 finite-grid rows")
    return {"rows": total, "profiles": len(seen)}


def calibration(root):
    groups, identities = {}, set()
    for r in records(root, "data/kappa_strength_raw.csv"):
        k = (int(r["n"]), number(r["kappa"]))
        ident = k + (int(r["replication"]),)
        require(ident not in identities, "Duplicate calibration record")
        identities.add(ident)
        groups.setdefault(k, []).append(r)
        rssr, rssu = number(r["RSS_restricted"]), number(r["RSS_unrestricted"])
        close(r["partial_R2"], (rssr-rssu)/rssr, "Partial R2")
        close(r["first_stage_F"], ((rssr-rssu)/2)/(rssu/(k[0]-13)), "Nested F")
    saved = {}
    for r in records(root, "data/kappa_strength_summary.csv"):
        k = (int(r["n"]), number(r["kappa"]))
        require(k not in saved and k in groups, "Calibration summary keys")
        g = groups[k]
        require({int(x["replication"]) for x in g} == set(range(1, 101)) and len(g) == 100, "Calibration count")
        for prefix, source in (("F", "first_stage_F"), ("partial_R2", "partial_R2")):
            z = sorted(number(x[source]) for x in g)
            for label, v in (("mean", statistics.mean(z)), ("median", statistics.median(z)),
                             ("sd", statistics.stdev(z)), ("min", z[0]), ("max", z[-1]),
                             ("p10", z[9]+.9*(z[10]-z[9])), ("p90", z[89]+.1*(z[90]-z[89]))):
                close(r[prefix+"_"+label], v, "Calibration summary")
        close(r["n_success"], 100)
        close(r["n_failed"], 0)
        saved[k] = r
    require(set(saved) == set(itertools.product((500,1000), KAPPAS)), "Calibration design")
    return saved


def table_text(root, name):
    p = root / "data/reference_tables" / name
    if not p.is_file():
        raise MissingEvidence(str(p.relative_to(root)))
    return p.read_text(encoding="utf-8")


def displayed_tables(root, saved, calibrated):
    checked = rows_checked = 0
    tau = kappa = None
    for line in table_text(root, "table_main_performance.tex").splitlines():
        if not any(" & "+e+" &" in line for e in ("Oracle-GMM", "Full-GMM", "DML-IVQR")):
            continue
        fields = [re.sub(r"\\SetCell\[[^]]*\]\{[^}]*\}", "", f).replace("\\\\", "").strip()
                  for f in line.split("&")]
        if fields[0]: tau = number(fields[0])
        if fields[1]: kappa = number(fields[1])
        e = fields[2] + ("-BC" if fields[2] == "DML-IVQR" else "")
        r = saved[(1000, tau, kappa, e)]
        require(len(fields) == 8, "Main table schema")
        for name, value in zip(("Bias", "MAE", "RMSE", "Coverage", "median_grid_accepted_set_measure"), fields[3:]):
            close(r[name], value, name, .00050000001)
            checked += 1
        rows_checked += 1
    require(rows_checked == 36 and checked == 180, "Expected 36 main table rows / 180 values")
    cal_values = 0
    for line in table_text(root, "table_strength_calibration.tex").splitlines():
        if not re.match(r"^(500|1000) &", line): continue
        f = [x.strip().replace("\\\\", "").strip() for x in line.split("&")]
        require(len(f) == 6, "Calibration table schema")
        r = calibrated[(int(f[0]), number(f[1]))]
        for field, value, tol in (("F_median", f[2], .00500000001),
                                  ("partial_R2_median", f[4], .00050000001)):
            close(r[field], value, field, tol); cal_values += 1
        for prefix, pair, tol in (("F", f[3], .00500000001), ("partial_R2", f[5], .00050000001)):
            lo, hi = pair.split("--")
            close(r[prefix+"_p10"], lo, prefix, tol)
            close(r[prefix+"_p90"], hi, prefix, tol)
            cal_values += 2
    require(cal_values == 48, "Expected 48 calibration table values")
    return {"main_performance_values": checked, "strength_calibration_values": cal_values,
            "scope": "Two displayed main numeric tables; copied W3 TeX, not rasterized figures or all appendix tables"}


def verify(root, unsealed=False):
    checks = []
    def run(name, fn, required=True):
        try:
            detail = fn()
            checks.append({"check": name, "status": "PASS", "required": required, "detail": detail})
            return detail
        except MissingEvidence as e:
            checks.append({"check": name, "status": "NOT_VERIFIABLE", "required": required, "detail": str(e)})
        except Exception as e:
            checks.append({"check": name, "status": "FAIL", "required": required, "detail": str(e)})
        return None
    if unsealed:
        checks.append({"check": "sha256_inventory", "status": "SKIP", "required": False,
                       "detail": "Explicit construction-only --allow-unsealed; not a release integrity pass"})
    else:
        run("sha256_inventory", lambda: integrity(root))
    result = run("main_estimator_records", lambda: main_records(root))
    if result is not None:
        data, groups = result
        checks[-1]["detail"] = {"rows": len(data), "cells": len(groups)}
        saved = run("main_summary_consistency", lambda: summaries(root, groups))
        if saved is not None: checks[-1]["detail"] = {"cells": len(saved), "all_summary_fields_checked": True}
        run("false_candidate_evaluations", lambda: power(root, data))
        run("finite_grid_records", lambda: profiles(root, data))
    else:
        saved = None
        for name in ("main_summary_consistency", "false_candidate_evaluations", "finite_grid_records"):
            checks.append({"check": name, "status": "NOT_VERIFIABLE", "required": True,
                           "detail": "Main record prerequisite failed/unavailable"})
    cal = run("strength_calibration_saved_arithmetic", lambda: calibration(root))
    if cal is not None: checks[-1]["detail"] = {"rows": 800, "cells": len(cal), "refitted": False}
    if saved is not None and cal is not None:
        run("displayed_main_numeric_tables", lambda: displayed_tables(root, saved, cal))
    else:
        checks.append({"check": "displayed_main_numeric_tables", "status": "NOT_VERIFIABLE", "required": True,
                       "detail": "Summary/calibration prerequisite unavailable"})
    for name, status, detail in (
        ("historical_stochastic_replay", "NOT_VERIFIABLE", "Main worker penalty states not recovered; no simulation run"),
        ("complete_selected_case_certificate_replay", "NOT_VERIFIABLE", "Exact-face prerequisite missing; numerical inputs not bundled; no certificate pipeline run"),
        ("raw_domain_profile_reconstruction", "NOT_VERIFIABLE", "Only domain summaries bundled; original raw domain archive exists separately"),
        ("historical_R_installation", "SKIP", "No R install or historical runner invoked"),
        ("inferential_calibration", "NOT_VERIFIABLE", "Nominal chi-square validity not established by archived arithmetic")):
        checks.append({"check": name, "status": status, "required": False, "detail": detail})
    status = "FAIL" if any(c["status"] == "FAIL" for c in checks) else "NOT_VERIFIABLE" if any(
        c["required"] and c["status"] != "PASS" for c in checks) else "PASS"
    return {"archived_verification": status, "sealed": not unsealed, "public_publication": "NOT_READY",
            "scope": "Archived-output arithmetic and inventory only; not complete reproducibility", "checks": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, help="Optional new report file; refuses overwrites and writes inside sealed repository")
    parser.add_argument("--allow-unsealed", action="store_true", help="Construction only: explicitly skip manifest check")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.output:
        require(not args.output.exists(), "Refusing to overwrite a verification report")
        require(not args.output.resolve().is_relative_to(root), "Write reports outside the frozen candidate")
    report = verify(root, args.allow_unsealed)
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output: args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["archived_verification"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
