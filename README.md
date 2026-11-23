# Controlled Instrument-Relevance Sensitivity in High-Dimensional IVQR: A Monte Carlo Study

**Private publication candidate — NOT_READY for public distribution.** This is the complete selected code/evidence package, not the earlier tooling-only ZIP. Historical-source, data/asset permissions and both-author release approval remain unconfirmed. No GitHub publication, v1.0.0 release or journal submission is claimed.

**Authors (as listed in frozen W3):** Umurzokov Olimjon Umidjon ugli and Kostaev Umidjon Umirzakovich. **Affiliation:** Tashkent State University of Economics, Tashkent, Uzbekistan. These are manuscript metadata, not new coauthor publication attestations. Public email/ORCID details are not added.

## Study and design

The study varies excluded-instrument relevance while preserving the documented joint treatment/outcome-disturbance distribution under a Gaussian compensating-noise construction. It compares complete preserved Oracle-GMM, Full-GMM and pivotal-penalty DML-IVQR implementations using point accuracy, direct truth acceptance, false-candidate rejection and finite-grid informativeness. It proposes no new estimator or inferential theorem and does not isolate the causal effect of regularization.

The frozen main design has n=500/1000, quantiles .10/.25/.50/.75/.90, kappa=1/.50/.25/.10, 100 candidate controls and 500 replications per design. Point estimates minimize over 41 candidates on [-1,3] at step .1. Direct tests at truth and six false offsets use the retained nominal chi-square(2) cutoff. Truth acceptance is not membership coverage of the separately stored finite-grid set, and raw rejection is not equal-size power.

## Install and verify

Use **Python 3.11**. Core verification and tests use its standard library; `requirements.txt` documents that no pip packages are needed. From the repository root:

```sh
python -B -m unittest discover -s tests -v
python -B scripts/verify_evidence.py
python -B scripts/export_findings.py --output ../findings-new.json
```

Use a new output filename. Utilities refuse overwrites and writes inside the frozen repository. `-B` avoids cache files changing its inventory. The verifier checks **60,000 estimator records, 360,000 false-candidate evaluations, 2,460,000 finite-grid records**, complete main summaries, saved calibration arithmetic, **180 displayed performance values plus 48 calibration values**, and SHA256/byte integrity. Missing required evidence yields NOT_VERIFIABLE; inconsistent evidence yields FAIL; either gives a nonzero exit. PASS is archived-output consistency, not historical stochastic replay or statistical validity.

To reproduce the bundled descriptive figures and table views in a separate directory:

```sh
python -m pip install -r requirements-figures.txt
python -B scripts/render_outputs.py --output ../views-new --compare-bundled
```

The plotting dependencies are an explicit **new reporting environment**, not upgrades to historical estimators. It was tested with the recorded pinned packages on Windows. Exact SVG-byte comparison can depend on platform/fonts; omit `--compare-bundled` to reconstruct on another platform without claiming bitwise graphics identity. Five SVGs and two CSV views are derived solely from archived summaries. They are reconstructed views, not pixel-identical replacements for original W3 graphics. No new data, estimation, simulation or cutoff calibration occurs.

## Repository map

| Path | Purpose |
|---|---|
| `src/` | Six byte-preserved scientific modules; original environment guard; portable definition loader. |
| `config/` | Actual unchanged Monte Carlo configuration and historical package-version inventories. |
| `data/` | Saved calibration evidence and immutable copies of W3's two main numeric table references. |
| `results/main/` | All twelve archived main output files, with six large CSVs stored losslessly as gzip. |
| `results/diagnostics/` | Minimal article-cited domain and selected numerical-policy summaries. |
| `results/views/`, `figures/` | Reconstructed CSV views and SVG figures; source values remain archived separately. |
| `scripts/`, `tests/` | Safe verification/reporting tools and essential adversarial tests. |
| `manuscript/` | Frozen W3 identity and access status; no PDF or manuscript prose is distributed without preprint/asset authority. |
| `docs/`, `.github/workflows/` | Reproducibility/rights boundaries and read-only automated verification. |

## Software and limits

The original implementation records Windows R 3.4.3, quantreg 5.34, hdm 0.2.0, hqreg 1.4, mvtnorm 1.0-6 and doSNOW 1.0.16. Full recorded versions are in `config/`. The portable R loader preserves the original environment checks and only loads definitions after an explicitly supplied historical environment passes. It does not run a fit or provide an exact historical replay command. No historical guard is weakened.

Historical stochastic replay and complete selected-case numerical certification remain **NOT_VERIFIABLE**. Main worker penalty states and a referenced exact-face prerequisite are unresolved. The non-finite mixed density, actual proxy/projection/same-sample rules and numerical rank sensitivity limit theoretical interpretation. See [reproducibility](docs/REPRODUCIBILITY.md), [dependencies](docs/DEPENDENCIES.md) and [limitations](docs/LIMITATIONS.md).

## Citation, provenance and rights

Use `CITATION.cff` for this proposed software package, and identify the paper as an unpublished manuscript unless its actual publication status changes. No DOI or accepted-journal status is invented.

Historical project: [U-Olim/DML-IVQR_Master_Thesis](https://github.com/U-Olim/DML-IVQR_Master_Thesis), checked revision `acbd06923fc6f1d67a8262b3bc7ad9fe9cb3831a`. The study builds on [Chen, Huang and Tien's DML-IVQR work](https://arxiv.org/abs/1909.12592) and [upstream executable code](https://github.com/FieldTien/DML-IVQR). Preserve this attribution; public visibility is not redistribution permission.

`LICENSE` is the original limited-scope notice, not a blanket grant for borrowed wrappers, output data or manuscript assets. [Third-party notices](docs/THIRD_PARTY_NOTICES.md) and [release status](docs/RELEASE_STATUS.md) identify remaining holds. The target URL is `https://github.com/U-Olim/IVQR-Instrument-Relevance-Monte-Carlo`; the lookup returned 404 during preparation, so public access is not verified. Publication is conditional on actual rights and both-author approval; a local commit or passing CI cannot supply them.
