# Configuration, execution, and artifact contracts

Read when implementing experiment configs, output writers, aggregation, or reproducible plotting. Apply the relevant contracts to the project's stack; these are not a request to introduce a new framework.

## Configuration and paths

Prefer versioned `.yaml` files for new experiment and plotting configs. Use safe YAML loading and validate the parsed structure. Preserve another format when required by an existing consumer or established tooling; for example, a plotting tool that only accepts JSON should keep a JSON interface. This preference concerns configuration, not result formats or label-mapping metadata. For workflows that exist, give standard, quick, and sweep runs distinct named configs while sharing implementation.

Declare relevant inputs and protocol metadata, method/model choices, experimental variables, seeds, sample limits, resource settings, output location, variant identity, and optional post-processing. Keep presentation choices separate from data collection: recording more metrics than a figure displays should not require rerunning the experiment to change the figure.

Define and document precedence, usually `defaults < config < explicit CLI overrides`. Distinguish an omitted CLI option from an explicit false/zero value so parser defaults do not accidentally override config values. Validate unknown keys, types, ranges, duplicate experiment combinations, conflicting options, required files, and path-component identifiers before expensive computation. Avoid mutating the source config during temporary overrides.

Resolve project-config relative paths against one documented base, normally the repository root, including relative config paths supplied through CLI if that is the chosen convention. For a script directly in `scripts/`, this may be:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[1]
```

This depth is specific to that layout. After moving code into a package, use an explicit project-root/config mechanism or a valid installed-resource strategy rather than blindly copying `parents[1]`. Honor absolute external data/checkpoint paths when supplied. A standalone plot bundle uses its config directory as the relative-path base.

Log the resolved settings after all overrides, the command, device/task assignment, and relevant software/code version when available. For an uncommitted tree, a commit alone does not fully identify the executed code; record its dirty state or a suitable snapshot rather than implying otherwise. Do not serialize secrets from environment variables into provenance records.

## Sequential multi-seed experiments

When writing stochastic training/evaluation scripts, support one experiment invocation with an ordered seed list in YAML. For example, adapt these illustrative keys to the project's implemented interface:

```yaml
seeds: [11, 42, 123]
output_dir: runs/method_sweep
```

Validate a nonempty list of distinct integer seeds within the active libraries' supported range, rejecting booleans and duplicates. Execute seeds sequentially in the configured order by default; do not require users to edit the config or run a shell command separately for every seed. If existing tooling also accepts a single `seed`, define its precedence or reject conflicting `seed`/`seeds` inputs explicitly.

Before each seed, reset the random generators used by the project (e.g. Python, NumPy, framework CPU/GPU RNGs, sampler/DataLoader workers) and recreate mutable experiment state such as model initialization, optimizer, scheduler, scaler, and metric accumulators. Fresh processes per seed or a correctly isolated in-process loop are both valid. An explicitly requested continuation protocol is different from independent seed repeats. Record determinism settings and known nondeterministic operations rather than promising identical results on every device.

For each seed, run its required experiment tasks, record its actual seed and protocol, and persist completed records under `seed_<seed>/` before advancing to the next seed. Export `results.json`, `results.csv`, and `results.md` from the same records. Log the current seed and its position, such as `[INFO] Seed 42 (2/3)`, and keep runtime/failure context attributable to that seed.

After the required seeds finish, collect their saved results and group by every non-seed comparison dimension, such as method, model, dataset/split, hyperparameter setting, and metric. Compute cross-seed statistics only within comparable groups; never average different sweep settings or treat batches/samples as independent seeds. Include per-seed values and seed identities, expected/completed seed counts, mean, explicitly defined standard deviation, metric units, and relevant sample counts. For sample standard deviation (`ddof=1`), a single completed seed has undefined uncertainty; encode it as null/blank and explain it in Markdown rather than inventing zero.

Write the collected individual records as `summary/results.{json,csv,md}` and aggregated statistics as `summary/average_results.{json,csv,md}`. The brace notation denotes three separate files for each basename. Generate all formats from one canonical record/statistics collection; additional formats are welcome when useful. Keep machine-readable values unrounded and format human-readable tables for inspection.

Keep completed outputs if a seed fails. State whether the runner stops or continues, list failed/missing seeds, and never label a partial collection as a complete experiment. A deliberately produced partial summary must disclose its actual seed count for each group and remain distinguishable from the final summary. An optional aggregation-only command may rebuild summaries from compatible saved seed records without retraining; it must not silently include unrelated executions.

## Training progress and logging

Use `tqdm` for training epochs or batches when progress is meaningful. Show the current epoch/step, total work when known, and a small set of useful metrics through the description/postfix; do not replace it with per-batch print statements. Keep refresh frequency reasonable. Disable animated bars when output is redirected or non-interactive, and use concise periodic log updates instead. In distributed or parallel execution, let the main process own the terminal progress display.

Use a run-specific file logger for full diagnostics and a concise console handler for user-facing status. Capture Python warnings into logging where appropriate, and route known non-actionable categories/messages to the file handler only. Apply such filtering to the console handler, so these records still reach the log. Configure relevant third-party loggers similarly, avoiding duplicate propagation. Do not blanket-ignore all warnings, redirect all stderr away from the user, or hide a warning merely because it is frequent; issues affecting correctness, numerical validity, unavailable resources, or recoverable failures remain visible.

Give status messages consistent prefixes: `[INFO]` for milestones and output locations, `[SUCCESS]` after the named operation succeeds, `[WARNING]` for an actionable issue or degraded behavior, and `[FAIL]` for a failed operation. File records should also include timestamps, level, and task/process identity when needed. Preserve exception details in the file and show the terminal a concise failure reason plus the log path. Successful training and successful plotting are separate statuses; do not report overall success after required post-processing fails.

Coordinate the console logger with `tqdm` using a compatible logging redirect or `tqdm.write` for occasional messages, rather than letting ordinary prints break the active bar. Progress indicators themselves need no status prefix, and machine-readable stdout must remain clean when it is an explicit CLI interface; put human-readable status on stderr in that case.

## Output hierarchy and collision behavior

One multi-seed workflow might produce:

```text
runs/<workflow>/
└── idea_<variant>/                 # Optional experiment intention
    └── run_<timestamp-or-id>/      # Distinct execution when reruns coexist
        ├── resolved_config.yaml
        ├── run_<timestamp>.log
        ├── seed_11/
        │   ├── results.json
        │   ├── results.csv
        │   └── results.md
        ├── seed_42/
        │   └── ...
        ├── seed_123/
        │   └── ...
        └── summary/               # Final complete aggregation
            ├── results.json
            ├── results.csv
            ├── results.md
            ├── average_results.json
            ├── average_results.csv
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

Generate formats from one canonical collection of records. JSON preserves types and nested values, CSV supports tabular analysis, and Markdown supports inspection/reporting. Multi-seed workflows provide all three for individual and aggregate results as specified above; simpler workflows can use the formats their consumers need. Do not maintain three separate computations. Retain full precision in machine-readable data and round only display values.

Specify which records are aggregated and which are excluded or missing. Record seed count, sample/task unit, and whether aggregation is weighted. Name the uncertainty measure: population/sample standard deviation, standard error, or confidence interval. Do not silently equate these or report uncertainty from an insufficient number of runs as measured zero. Preserve per-seed data so aggregation can be checked later.

## Independent replot bundle

When plotting is part of a training/evaluation workflow, run it automatically after successful computation, aggregation, and result persistence by default. Use the same plotting implementation for the automatic step and a standalone plotting entrypoint. Allow the automatic step to be disabled through a documented config/CLI option when appropriate. If plotting fails, retain the completed experiment outputs, report the plotting failure separately, and provide the standalone retry command.

The standalone entrypoint accepts saved chart-ready data and an editable plot config, including style and series-selection parameters. Changing those parameters must not require training, evaluation, or loading model checkpoints. Document both the automatic behavior and the independent redraw command in the workflow guide.

For generated research figures, put the following together under the run's plot directory:

```text
plots/
├── comparison_data.csv
├── comparison_config.yaml
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

Check meaningful behavior for what changed: an implemented entrypoint loads, invalid configs fail early, an explicit CLI override wins without editing the config, paths work under the documented base, distinct executions remain isolated, and smoke outputs match the documented contract. When changing progress/logging, check that known non-actionable warnings reach the file but not the console, actionable warnings/failures remain visible with suitable prefixes, and redirected output has no animated progress artifacts. Check incremental/partial behavior when changing long-running orchestration, aggregation on known small records when changing statistics, and both automatic post-run plotting and independent redraw when changing plot orchestration or bundles.

Use existing project checks where possible. Add automated tests for consequential parsing, aggregation, resume, or orchestration logic when warranted; do not add tests merely to assert directory names or Markdown headings. If required data, dependencies, or hardware are missing, perform available static checks and state which runtime behavior remains unverified.

For implemented multi-seed orchestration, use a bounded fixture or small run to check configured seed order, independent initialization, separate incremental outputs, and matching records across JSON/CSV/Markdown. Check aggregation against a small known set, including separate sweep groups, a missing/failed seed, and the single-seed uncertainty case. These checks verify generated project code when that code is implemented; the illustrative YAML here does not itself run an experiment.
