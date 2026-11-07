---
name: research-project-workflow
description: Build reproducible research and machine-learning project workflows covering file organization, coding conventions, YAML configs, sequential multi-seed experiments, result exports, plotting, and step-by-step command-line guides with Conda environments. Use when creating or extending research code, documenting how to prepare and run experiments, or reviewing/refactoring these workflows. For focused edits, apply relevant conventions without reorganizing the whole repository.
---

# Research Project Workflow

Use this skill to organize research files, implement consistent experiment code, and write command-by-command reproduction guides. The deliverable is a runnable, documented workflow with traceable inputs and results.

## Scope and scale

- Follow the user's chosen stack, layout, and existing repository conventions. The directory names below are defaults for research projects, not requirements for every software project. Use Conda exclusively to create and manage Python environments; see the environment rule below.
- For a new project, create only the layers its first runnable workflow needs. For an added experiment, extend its guide, config, entrypoint, and output contract together. For an architecture review, report evidence and recommendations; change files only when implementation or refactoring is requested.
- Keep a small one-off script small. Do not create empty `src/`, `tests/`, research-note directories, fictitious CLI entrypoints, or a framework merely to resemble a template.
- On an existing project, inspect tracked files and relevant local/ignored assets as well as documentation. Inspect paths, sizes, and representative metadata rather than loading datasets or weights. Distinguish current working-tree state from committed or remote state.

## Workflow

1. **Map the real workflow.** Identify the input assets, experiment protocol, shared implementation, executable entrypoints, configuration consumers, result units, and documentation. Note missing inputs and broken links without inventing working components.
2. **Choose the smallest layout.** Read [references/layout-and-docs.md](references/layout-and-docs.md) when scaffolding, moving files, or writing guides. Keep a short mapping for each affected workflow:

   `README / guide → config → entrypoint → inputs → run outputs → summary / plots`

   A guide may cover related configurations, and several configurations may share one implementation. Align names semantically rather than duplicating code to force one file per experiment.
3. **Implement the file contracts.** Read [references/experiment-contracts.md](references/experiment-contracts.md) when adding configuration, experiment execution, aggregation, or plotting. Resolve paths consistently, isolate runs, record resolved settings, and make outputs reflect the experiment units.
4. **Write the runnable guide.** Read [references/step-by-step-guides.md](references/step-by-step-guides.md) whenever creating or updating setup/run instructions. Give ordered commands for Conda setup, data/checkpoint preparation, validation, smoke runs, formal runs with each relevant config, CLI overrides, and independent replotting. Each step explains its purpose, prerequisites, working directory/environment, and observable success check. Link shared preparation instructions rather than duplicating them.
5. **Keep documentation and Git boundaries consistent.** Update affected commands, imports, config paths, packaging declarations, README links, guide examples, and ignore rules together. Reuse dependency declarations within the Conda environment. Keep substantial data, weights, generated runs, caches, and private notes outside ordinary Git by default; preserve deliberate release artifacts and existing data-versioning arrangements.
6. **Verify the changed chain.** Use checks appropriate to the implementation: entrypoint/import checks, config validation, a bounded smoke run when inputs are available, output inspection, and independent replotting when plots were added. Check guide commands against the actual CLI and inspect references and ignore behavior. Report missing assets, unavailable hardware, and checks not run explicitly; do not present an unexecuted command as verified.

## Project workflow rules

### Use Conda and teach the workflow step by step

- Create and manage Python environments only with Conda. Prefer a maintained `environment.yaml` for new projects, or document `conda create` with a justified Python version and explicit activation. Do not offer `venv`, virtualenv, Poetry/uv-managed environments, or system-Python installation as alternative setup paths. If Conda is unavailable, state that prerequisite and provide appropriate installation guidance; do not silently substitute another manager.
- Install dependencies into the named Conda environment. Packages unavailable through suitable Conda channels may use `python -m pip` inside that environment; this does not create a second environment. Never install project packages into `base` or system Python. Keep existing dependency declarations consistent rather than inventing a new incompatible source of versions.
- Guides must teach the exact command sequence, not just describe what users should do. Start with environment setup and input preparation, then demonstrate small validation, formal execution, different YAML configs, supported CLI overrides, sequential seeds, output inspection, and independent redraw where relevant. Do not invent flags, scripts, download URLs, or successful results. Detailed requirements and adaptable examples are in [references/step-by-step-guides.md](references/step-by-step-guides.md).

### Separate stable instructions from implementation and assets

- `README.md` is the project map and shortest startup path: goal, installation/preparation links, minimal command, protocol summary, and verified baseline when available. Put detailed task-specific instructions in `guide/` or the repository's equivalent.
- `configs/` declares run intent. Prefer `.yaml` for new experiment and plotting configs; retain an existing format when required by the consumer or established tooling. Separate experiment collection settings from visualization settings. Use distinct named configurations for standard runs, quick checks, and sweeps when those workflows exist.
- `scripts/` contains clearly named executable entrypoints such as `evaluate_<method>.py` or `plot_<experiment>.py`. A few self-contained scripts are reasonable; extract shared code into an actual package when reuse or complexity warrants it.
- Keep input data, checkpoints, run outputs, untested ideas, and process notes distinct from executable code and stable guides. Preserve upstream dataset identifiers and version the mappings that interpret them.

### Make experiment intent visible and portable

- Use one documented path base for project configuration, normally the repository root. Do not depend on whichever shell directory happened to launch the command. A movable plot bundle instead resolves paths relative to its saved config.
- Define configuration precedence, normally defaults < config file < explicit CLI flags. Reject unknown fields and invalid values/combinations before expensive work. Temporary CLI overrides do not rewrite the baseline configuration.
- Keep run identifiers safe as path components. Separate incompatible reruns so stable filenames cannot silently mix or overwrite distinct experiments.
- Log the final resolved configuration and task assignment. Preserve enough context in results to explain the method, inputs, seed, sample scope, hyperparameters, metrics, and runtime without shell history.

### Keep training progress and terminal output readable

- Use `tqdm` for training progress when suitable, showing the epoch/step and useful metrics without printing every batch. Disable animated output in non-interactive runs and avoid competing progress bars from parallel workers.
- Route known non-actionable warnings and verbose diagnostics to the run's log file instead of the terminal. Keep actionable warnings and failures visible; do not suppress warnings globally or discard their diagnostic context.
- Prefix status messages appropriately, for example `[INFO]`, `[SUCCESS]`, `[WARNING]`, and `[FAIL]`. Coordinate console logging with progress bars so messages do not corrupt the display. See the progress and logging contract in [references/experiment-contracts.md](references/experiment-contracts.md).

### Make results auditable and reusable

- For stochastic training/evaluation, expose an ordered seed list in the experiment config, such as `seeds: [11, 42, 123]`. One invocation runs those seeds sequentially by default, resets random generators and experiment state for each seed, saves each seed's results separately, then aggregates comparable records across seeds. Read the multi-seed contract in [references/experiment-contracts.md](references/experiment-contracts.md) when implementing this workflow.
- Match output hierarchy to actual units: workflow, optional variant, distinct execution, optional seed, then aggregate. Omit unnecessary levels; separate smoke output from formal output.
- Save completed task results incrementally for long runs. For multi-seed experiments, write both per-seed results and final cross-seed statistics as `.json`, `.csv`, and `.md` from the same records; additional formats may serve other consumers. Retain full precision in machine-readable files and round only display values.
- Keep timestamped logs and stable result names inside an isolated execution. Distinguish partial results from completed summaries; an existing `summary/` directory alone does not prove completion.
- Record the aggregation population, number of seeds/tasks/samples, metric units, and uncertainty definition. Do not copy the source project's population-standard-deviation choice into every experiment.
- When a training/evaluation workflow produces research figures, normally run plotting automatically after successful computation and result persistence. Also expose a separate plotting entrypoint that reads saved data and an editable plot config, so changing presentation parameters does not restart training/evaluation. Save full-precision chart-ready data, plot config, runnable plotting code, and final images together; include required local helpers or document dependencies.

### Preserve research and version-control boundaries

- Stable reproduction facts belong in guides; hypotheses and proposed experiments belong in dated idea notes. Current implementation explanations, stage status, and historical investigations can be separate notes when needed.
- Shared `.gitignore` rules apply to all clones; `.git/info/exclude` is local to one clone. Choose deliberately for private notes rather than assuming they are equivalent. Ignoring already-tracked files does not untrack them.
- This skill does not call for commits, pushes, uploads, deleting assets, or removing tracked files. Perform such actions only within the user's requested scope. Do not install this skill into a user's environment merely because a project uses it.

## Completion and review

For implementation, briefly report the resulting layout, affected workflow mapping, verification performed, and remaining prerequisites. A review should identify concrete paths and broken contracts, distinguish observations from proposals, and prioritize fixes by their effect on running or reproducing experiments. Save a separate architecture report only when requested or useful for the agreed deliverable.

Before finishing, check that the affected workflow has discoverable commands and outputs, small-run versus formal-result boundaries are explicit, existing callers still resolve, and the versioned files are sufficient to reacquire excluded assets. Apply only relevant checks; do not expand a focused change into a full repository audit.
