# Reproducibility and supported commands

The supported workflow verifies immutable archived records with Python 3.11 standard-library tools. It does not rerun the Monte Carlo experiment. Source CSVs and their scalar values remain unchanged; six large CSVs use deterministic lossless gzip. Their stored and decompressed source hashes are recorded separately. All other retained historical code/data/table files are copied byte-for-byte, with source-to-repository mapping in `RELEASE_MANIFEST.csv`.

Run the README commands from the repository root. The adversarial tests check missing/corrupt/unlisted evidence, unsafe manifest paths, changed truth decisions, duplicate records and nonfinite values. Full verification checks 60,000 estimator records, 360,000 false-candidate records, 2,460,000 finite-grid records, all main summary fields, 800 calibration records and 228 displayed main-table values. No original R or scientific Python module is imported by those checks. Differences exceeding 2e-10 absolute tolerance fail; table checks use half a unit at the displayed precision. Missing files receive NOT_VERIFIABLE, not PASS.

The descriptive exporter creates a new external JSON view from a reverified archive. The plotting command creates five SVG and two CSV views in a new external directory. It refuses overwrites and writes inside the frozen repository. Matplotlib and its explicit pinned new reporting dependencies are separate from historical estimator dependencies. Source values are not rounded before plotting. These are reconstructed descriptive views, not pixel-identical paper graphics; no changed statistic or repaired result is introduced.

The release inventory covers all repository payload files except itself; root `.git` metadata is excluded. `.gitattributes` prevents newline conversion. A matching manifest establishes file identity, not authorship, a redistribution grant, original execution provenance or inferential validity.

| Capability | Status / scope |
|---|---|
| Archived-output verification | Executable, PASS when the supplied files pass all required checks. |
| New descriptive reporting | Executable from saved scalar summaries; no refitting. |
| Historical R reporting runner | Not offered as a supported command; original freeze/output guards are not bypassed. |
| Exact historical stochastic replay | NOT_VERIFIABLE: main worker penalty states are incomplete; seed 675 is insufficient. |
| Complete selected-case certificate replay | NOT_VERIFIABLE: numerical inputs/certificates are not bundled and exact-face prerequisite remains unlocated. |
| Inferential calibration | NOT_VERIFIABLE: a nominal chi-square decision rule is not a validated sampling law. |

Raw domain profiles/primitives and incomplete pilots are not distributed; only the article-cited final diagnostic summaries are retained. Their exclusion is explicit and does not imply they are globally lost. CI runs deterministic tests and saved-data reporting only. A workflow file or local success does not establish an actual hosted GitHub run; public CI is pending clearance and publication.
