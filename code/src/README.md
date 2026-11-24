# Preserved implementation

The six research modules are byte-identical to their historical source files, with exact hashes in the release manifest. No solver, penalty, residual rule, data generator, estimator or statistical conclusion has been changed. The environment guard is also preserved byte-for-byte.

`load_implementation.R` is a new path/definition loader, not a new estimator. It takes a repository root and an explicitly supplied historical extension-environment root, applies the original R/library/package guard, loads the unchanged actual configuration and these six modules into one environment, and returns that environment without fitting or generating data. Relative source paths resolve from this repository. Historical runtime installation and execution are NOT_VERIFIABLE here; the loader was inspected statically, not used to run research.

The old full-experiment launchers are deliberately not distributed or called by CI. No automatic simulation command is provided. This avoids suggesting that a parent seed and relocated code can reproduce missing historical worker states. See docs/DEPENDENCIES.md for original versus new verification/reporting dependencies.
