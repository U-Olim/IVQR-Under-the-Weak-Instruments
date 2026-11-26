# Earlier cleanup and verification (24 November 2026)

This is the historical cleanup record, including its original counts and verification claims. The subsequent full-tree audit, editorial-source consolidation and current verification are recorded in [audit/report.txt](audit/report.txt). Current submission filenames use underscores as documented in the root README; no dated correction directory is retained.

Prepared locally on 24 November 2026. No simulation, pilot, recalibration, estimator execution, push, publication or submission was performed.

## Selected source and preservation

The latest available W5 master from `journal_submission/final_article/` is now `article/main.tex`. The prior W5 build recorded 33 pages. `article/review.tex` only defines the existing anonymity flag and inputs the master. No competing manuscript master remains.

A complete external copy, including Git metadata and untracked files, was created before cleanup: `IVQR-precleanup-20261124-104555` in the system temporary directory. All 4,157 original payload files were compared with that backup by SHA-256 before removal. The backup contains the original manuscript versions, PDFs, runtime, reports and original Git state; retain it until submission preservation is complete. Detailed original inventory and verification/build records are stored there, outside the publication project.

All 47 implementation, configuration, frozen evidence, test and reporting files were relocated byte-for-byte into `code/`. The code manifest was scoped to this subtree, retaining original provenance, source hashes and rights flags. Scientific algorithms, numbers, tables and figure assets were not changed. Manuscript edits update repository paths and the build comment, and condition the identifying availability URL on the existing anonymity flag. The named availability text is unchanged.

## Removed and retained material

Removed from the active tree: W3 source copies and runtime; W3/W4/W5 build products; duplicated and stale article PDFs; editorial revision/compilation/validation scripts and implementation reports; the obsolete manuscript metadata directory and availability draft. Nine unused files in the final-article tree were excluded: two RMSE images, two stale PDFs, an unused evidence-map appendix and four unused appendix tables. All remain in the external backup.

Retained: every selected scientific module, historical environment guard and loader, configuration/version inventories, main archives, calibration records, two numerical reference tables, article-cited diagnostic summaries, deterministic integrity tests and optional archived-data reporting utilities/views. Historical diagnostics with incomplete replay remain explicitly qualified. No additional pilot datasets, environments or release ZIPs were found in the active selected package.

## Final layout and counts

- `article/`: 33 source, bibliography, table and figure files.
- `code/`: 48 files, including the 47 unchanged payload files and revised manifest.
- `docs/`: 6 concise supporting documents, including this record.
- `submission/`: 2 freshly compiled PDFs.
- Root metadata and CI: 6 files.

Total payload files, excluding `.git`: **4,157 before; 95 after**. Historical Git commits remain intact. Ignore rules exclude LaTeX build products, Python caches, environments and temporary files. CI and README paths use the new structure; the R loader takes `code/` as its root.

## Verification

- Existing six deterministic adversarial tests: PASS.
- Sealed evidence verifier: PASS, including SHA-256 inventory, 60,000 estimator records in 120 cells, all main summaries, 360,000 false-candidate records, 2,460,000 finite-grid records, 800 calibration records, and 180 performance plus 48 calibration display values.
- Two displayed main numerical article tables match their retained reference copies byte-for-byte. All retained numerical tables, bibliography and figure assets match the W5 source backup.
- Both document builds use pdfLaTeX, Biber and two further pdfLaTeX passes with shell escape and package auto-install disabled. Final logs: no undefined citations/references, duplicate labels, Biber warnings or overfull/underfull boxes. The epstopdf shell-escape-disabled warning is benign; existing figure assets require no conversion.
- Named and anonymous PDFs: 33 pages each, exact copies of their fresh build outputs. The named first page was visually inspected. Anonymous extracted text was checked for author names, affiliation, contact identifiers and identifying repository URL/commit; PDF Author metadata is empty.
- Essential R loader targets and LaTeX dependencies exist. Source changes were checked against the selected W5 source. No credential or private machine-path patterns were found in inspected text payloads; intentional named-author contact metadata remains in the named source/PDF.

These checks establish archived consistency and document integrity. They do not establish exact historical stochastic replay, missing numerical certificates, nominal inferential validity or third-party distribution rights.

## Submission blockers

Target journal/anonymity requirements, both-author exact-scope approval, manuscript/output/asset and upstream-wrapper redistribution grants, public repository access and a permanent deposit identifier remain unresolved. An editor-approved anonymous evidence deposit is needed if required by the journal. See `RELEASE_STATUS.md` and `THIRD_PARTY_NOTICES.md`. Local retention is authorized by this cleanup request; public distribution has not been authorized or performed.
