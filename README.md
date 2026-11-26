# High-Dimensional IVQR under Weak Instruments

Research implementation, frozen numerical evidence and final article source.

- `article/`: authoritative `main.tex`, including the journal's curly-bracket abstract statement, bibliography, tables and figures. `review.tex` is a three-line anonymous wrapper around the same master; supplementary appendices are included in both PDFs.
- `code/`: preserved implementation, configuration, frozen evidence, verification scripts, minimal tests and optional reporting views.
- `docs/`: reproducibility, dependencies, limitations and rights status.
- `submission/`: only the current named and anonymous journal PDFs, compiled from that master.
- `scripts/`: manuscript build and read-only repository inventory helpers, separate from the frozen research implementation.
- `docs/submission_abstract.txt`: complete current abstract for the submission portal.
- `docs/audit/`: file-level cleanup decisions, dependency map and verification report.

From the repository root, with Python 3.11:

```sh
python -B -m unittest discover -s code/tests -v
python -B code/scripts/verify_evidence.py
```

These are deterministic archived-record checks; no simulations or estimator execution occurs. The evidence manifest covers `code/` only. Run the preserved R definition loader with `code/` as its root; it requires an explicitly supplied historical environment.

To build both versions with installed pdfLaTeX and Biber, use PowerShell from the repository root. The helper refuses existing output directories and keeps all build products outside the repository:

```powershell
./scripts/build_manuscripts.ps1
```

After checking the output, the canonical destinations are `submission/High_Dimensional_IVQR_Under_Weak_Instruments.pdf` (`main.pdf`) and `submission/High_Dimensional_IVQR_Under_Weak_Instruments_anonymous.pdf` (`review.pdf`). Build logs and dependency recorder files remain in the printed external output directory. The helper does not replace submission files automatically. EPS conversion is disabled; existing PDF/PNG figure assets require none.

For a fresh SHA-256 inventory, duplicate scan and LaTeX dependency check, supply a new external directory:

```powershell
python -B scripts/audit_repository.py . "$env:TEMP/ivqr-inventory-new"
```

The token-overlap scan flags possible near duplicates for inspection; matching numbers or shared text alone do not justify deleting scientific records. Git history and complete pre-cleanup working state are preserved in the external checkpoint recorded in [the current audit report](docs/audit/report.txt). The earlier cleanup history remains in `docs/CLEANUP.md`.

See [reproducibility](docs/REPRODUCIBILITY.md), [cleanup verification](docs/CLEANUP.md), [limitations](docs/LIMITATIONS.md) and [release status](docs/RELEASE_STATUS.md). Archived consistency does not establish historical stochastic replay or validate the nominal inference. No public release or submission is claimed. Preserve [third-party attribution](docs/THIRD_PARTY_NOTICES.md); redistribution grants and both-author publication approval remain unresolved.
