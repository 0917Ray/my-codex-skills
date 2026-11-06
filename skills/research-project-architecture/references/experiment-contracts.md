# Configuration, execution, and artifact contracts

Read when implementing experiment configs, output writers, aggregation, or reproducible plotting. Apply the relevant contracts to the project's stack; these are not a request to introduce a new framework.

## Configuration and paths

Keep stable experiment intent in versioned YAML/JSON or the repository's existing config format. For workflows that exist, give standard, quick, and sweep runs distinct named configs while sharing implementation.

Declare relevant inputs and protocol metadata, method/model choices, experimental variables, seeds, sample limits, resource settings, output location, variant identity, and optional post-processing. Keep presentation choices separate from data collection: recording more metrics than a figure displays should not require rerunning the experiment to change the figure.

Define and document precedence, usually `defaults < config < explicit CLI overrides`. Distinguish an omitted CLI option from an explicit false/zero value so parser defaults do not accidentally override config values. Validate unknown keys, types, ranges, duplicate experiment combinations, conflicting options, required files, and path-component identifiers before expensive computation. Avoid mutating the source config during temporary overrides.

Resolve project-config relative paths against one documented base, normally the repository root, including relative config paths supplied through CLI if that is the chosen convention. For a script directly in `scripts/`, this may be:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[1]
```

This depth is specific to that layout. After moving code into a package, use an explicit project-root/config mechanism or a valid installed-resource strategy rather than blindly copying `parents[1]`. Honor absolute external data/checkpoint paths when supplied. A standalone plot bundle uses its config directory as the relative-path base.

Log the resolved settings after all overrides, the command, device/task assignment, and relevant software/code version when available. For an uncommitted tree, a commit alone does not fully identify the executed code; record its dirty state or a suitable snapshot rather than implying otherwise. Do not serialize secrets from environment variables into provenance records.

## Output hierarchy and collision behavior

One multi-seed workflow might produce:

```text
runs/<workflow>/
└── idea_<variant>/                 # Optional experiment intention
    └── run_<timestamp-or-id>/      # Distinct execution when reruns coexist
        ├── resolved_config.json
        ├── run_<timestamp>.log
        ├── seed_11/
        │   ├── results.json
        │   └── results.csv
        ├── seed_42/
        │   └── ...
        └── summary/               # Final complete aggregation
            ├── results.json
            ├── results.csv
            ├── average_results.md
            └── plots/
```

Omit seed directories for deterministic single runs and variant layers without a real variant. A simpler project may use one unique output directory per execution. Stable `results.*` names are useful within that execution; timestamped logs alone do not protect results from overwrite.

Define what happens if an output already exists: choose a fresh execution directory by default, or use an explicitly requested overwrite/resume mode. A resume must check protocol/config compatibility and completed task identities. Do not combine incompatible old and new records or treat an earlier summary as the latest run's completion evidence.

For long runs, persist each completed task and its status; use atomic replacement for refreshed result files where practical. Keep incomplete data readable and label failures/partial execution. Publish a final summary only after its required task set is complete, or clearly name and mark a requested partial summary. A completion flag or manifest can make this explicit; the directory's existence cannot.

Use a separate temporary output for smoke tests, such as a fresh `/tmp/<project>-smoke-<id>/` or an equivalent platform path. Small-run metrics validate execution and output shape, not formal accuracy.

## Result records and aggregation

Choose fields that make each record interpretable without shell history:

| Context | Relevant fields |
| --- | --- |
| Identity | workflow, execution/variant ID, method, model, dataset/version/split |
| Protocol | label-map/class-name source, candidate/input scope, preprocessing or adaptation choices |
| Parameters | resolved experiment variables and hyperparameters, seed, sample limit |
| Resources | device, worker scope/count when it affects execution, duration |
| Measurements | sample count, metric name/unit, raw counts or numerators/denominators where meaningful, value |
| State | task identity, completed/failed status, error/log reference where needed |

Do not invent inapplicable fields. Reuse a resolved-config file for bulky shared context, but keep its reference unambiguous. Baseline and proposed-method results should use identifiable, compatible protocols; do not hide a protocol change in an aggregate table.

Generate formats from one canonical collection of records. JSON preserves types and nested values, CSV supports tabular analysis, and Markdown supports inspection/reporting; provide the formats with real consumers rather than maintaining three separate computations. Retain full precision in machine-readable data and round only display values.

Specify which records are aggregated and which are excluded or missing. Record seed count, sample/task unit, and whether aggregation is weighted. Name the uncertainty measure: population/sample standard deviation, standard error, or confidence interval. Do not silently equate these or report uncertainty from an insufficient number of runs as measured zero. Preserve per-seed data so aggregation can be checked later.

## Independent replot bundle

For generated research figures, put the following together under the run's plot directory:

```text
plots/
├── comparison_data.csv
├── comparison_config.json
├── plot_comparison.py
├── comparison.png
└── comparison.pdf                 # For publication/report use
```

- Save the actual full-precision chart-ready values, including uncertainty magnitudes and their meaning, before plotting. Preserve the source-result reference and aggregation definition.
- Save the effective plotting config, including series selection, labels, style, input path, and output formats. Resolve bundle paths relative to this config so moving the bundle or changing shell directory does not break it.
- Save runnable plotting code and any project-local helpers it requires, or make the script standalone. State external dependency/version requirements when material; copying a script that imports unavailable private project modules is not independent replotting.
- Snapshot code/config/data for this execution so later default or source-code changes do not redefine an old figure. Do not embed chart values only in plotting calls.
- Verify by redrawing from saved data/config into a separate temporary destination, ideally from another working directory. If independence is uncertain, copy the bundle to a temporary location and check it there. This should not access the dataset, model, original training log, or expensive evaluation.

## Focused verification

Check meaningful behavior for what changed: an implemented entrypoint loads, invalid configs fail early, an explicit CLI override wins without editing the config, paths work under the documented base, distinct executions remain isolated, and smoke outputs match the documented contract. Check incremental/partial behavior when changing long-running orchestration, aggregation on known small records when changing statistics, and independent redraw when changing plot bundles.

Use existing project checks where possible. Add automated tests for consequential parsing, aggregation, resume, or orchestration logic when warranted; do not add tests merely to assert directory names or Markdown headings. If required data, dependencies, or hardware are missing, perform available static checks and state which runtime behavior remains unverified.
