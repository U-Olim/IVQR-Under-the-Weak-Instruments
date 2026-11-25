# High-Dimensional IVQR under Weak Instruments

Research implementation, frozen numerical evidence and final article source.

- `article/`: authoritative `main.tex`, bibliography, tables and figures. `review.tex` is a three-line anonymous wrapper around the same master.
- `code/`: preserved implementation, configuration, frozen evidence, verification scripts, minimal tests and optional reporting views.
- `docs/`: reproducibility, dependencies, limitations and rights status.
- `submission/`: named and anonymous PDFs compiled from the current master.

From the repository root, with Python 3.11:

```sh
python -B -m unittest discover -s code/tests -v
python -B code/scripts/verify_evidence.py
```

These are deterministic archived-record checks; no simulations or estimator execution occurs. The evidence manifest covers `code/` only. Run the preserved R definition loader with `code/` as its root; it requires an explicitly supplied historical environment.

To build with an installed LaTeX distribution (pdfLaTeX and Biber), use a new external build directory:

```powershell
$build = Join-Path ([IO.Path]::GetTempPath()) ("ivqr-article-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $build | Out-Null
Set-Location article
pdflatex -no-shell-escape -halt-on-error -output-directory="$build" main.tex
biber --input-directory "$build" --output-directory "$build" main
pdflatex -no-shell-escape -halt-on-error -output-directory="$build" main.tex
pdflatex -no-shell-escape -halt-on-error -output-directory="$build" main.tex
```

Repeat with `review` for the anonymous wrapper. Keep build products outside the repository; copy final PDFs into `submission/` as `High-Dimensional-IVQR-named.pdf` and `High-Dimensional-IVQR-anonymous.pdf`.

See [reproducibility](docs/REPRODUCIBILITY.md), [cleanup verification](docs/CLEANUP.md), [limitations](docs/LIMITATIONS.md) and [release status](docs/RELEASE_STATUS.md). Archived consistency does not establish historical stochastic replay or validate the nominal inference. No public release or submission is claimed. Preserve [third-party attribution](docs/THIRD_PARTY_NOTICES.md); redistribution grants and both-author publication approval remain unresolved.
