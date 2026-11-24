# Portable loader only. Preserved candidate algorithms and configuration are unchanged.
# This function loads definitions; it never draws samples or runs a fit.
load_preserved_ivqr <- function(repo_root = ".", historical_extension_root = NULL) {
  if (is.null(historical_extension_root)) {
    stop("Historical execution is NOT_VERIFIABLE from this package alone. Supply an explicitly authorized historical extension environment; no RNG work has started.")
  }
  repo_root <- normalizePath(repo_root, winslash = "/", mustWork = TRUE)
  scope <- new.env(parent = globalenv())
  source(file.path(repo_root, "src", "environment", "check_author_environment.R"), local = scope)
  scope$assert_author_environment(historical_extension_root, write_outputs = FALSE)
  source(file.path(repo_root, "config", "extension_config.R"), local = scope)
  files <- c("dgp_kappa.R", "author_oracle_wrapper.R", "author_full_wrapper.R",
             "author_bc_dml_wrapper.R", "metrics.R", "run_extension.R")
  for (name in files) source(file.path(repo_root, "src", name), local = scope)
  scope
}
