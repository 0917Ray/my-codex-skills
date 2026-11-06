# Layout and documentation patterns

Read when choosing directory responsibilities, deciding between scripts and a package, writing reproduction guides, or checking Git boundaries.

## Adaptable research layout

The tree shows possible responsibilities, not directories to create in advance. Reuse equivalent existing names such as `docs/`, `checkpoints/`, or `outputs/`.

```text
project/
├── README.md
├── .gitignore
├── <dependency declaration / lockfile>
├── configs/
│   ├── evaluation/          # Or training/, analysis/, etc., by consumer
│   │   ├── baseline.yaml
│   │   ├── method.yaml
│   │   ├── method_quick.yaml
│   │   └── method_sweep.yaml
│   └── visualization/
│       └── method_sweep.json
├── guide/
│   ├── preparation.md
│   └── method_sweep.md
├── scripts/
│   ├── evaluate_method.py
│   └── plot_method_sweep.py
├── src/<package>/          # Only if shared/package code exists
├── tests/                 # Only with meaningful implemented checks
├── data/                  # Local inputs, normally ignored
│   ├── downloads/          # Original archives, if retained
│   └── raw/<dataset>/      # Consumable upstream layout
├── models/                # Local checkpoints, normally ignored
├── runs/<workflow>/       # Generated experiment artifacts
├── Idea/                  # Optional dated hypotheses and plans
└── conversation_w_GPT/    # Optional local process knowledge
```

For a single analysis, `README.md`, a script, its config, and an ignored output directory may suffice. Add evaluation/visualization subdirectories when there are distinct consumers, not merely because the example has them.

## Entrypoints and shared implementation

A small number of scripts can contain the working implementation. Extract configuration, data access, methods, execution, or result handling into a package when multiple entrypoints reuse them or the boundaries become hard to maintain. Keep CLI entrypoints focused on argument parsing and orchestration after extraction.

Do not declare a console command whose target module does not exist. After packaging changes, check the actual import or installed command using the project's normal environment. Do not treat an empty `src/` or `tests/` directory as implemented functionality.

Name entrypoints with an action and object, and align guide/config/output names around the same workflow. A quick run and formal run should generally use the same implementation with different configuration rather than independently evolving demo code.

## README and guide responsibilities

The README should let a newcomer find the project goal, environment setup, input preparation, first small run, formal workflows, and major directories quickly. Include protocol constraints and a baseline result only when actually known; identify its setting and source. Link detailed explanations instead of duplicating them.

For each significant runnable workflow, provide a discoverable guide section or dedicated guide. A useful order is:

1. Purpose and protocol: what is measured, input/output scope, baseline definition, and important assumptions.
2. Prerequisites: environment, data, checkpoints, devices, and preparation links.
3. Smoke test: bounded input, seeds/devices/workers as appropriate, separate temporary output, expected files or success signals. Mark reduced-input metrics as unsuitable for formal reporting.
4. Formal run: exact command and intended configuration. State the working directory for commands.
5. Configuration: important fields, precedence, units, valid combinations, and whether resources such as workers are per task or global.
6. Outputs: a compact tree, file meanings, per-task versus aggregate granularity, completion/failure state, and statistical definitions.
7. Boundaries: known limitations, common errors, and independent replot commands when relevant.

Scale this to the task. A focused guide section is sufficient for a minor variant. Commands must match the implemented CLI; show expected behavior as such until it has been verified.

## Input preparation and environment

- Record the dataset/model source, version or revision where available, acquisition method, expected local path, and verification method. State optional inputs explicitly rather than reporting their absence as a failed setup.
- Keep archives separate from consumable data when archives are retained. Check archive contents before extraction or correcting an extra root directory; avoid destructive bulk rearrangement.
- Preserve upstream class IDs or directory names. Version small label maps, class names, split definitions, and other metadata that affect experimental semantics. Distinguish directory-label maps from text/prompt names when they differ.
- Declare dependencies using the project's established tooling. Pin research implementations to a release or commit when reproduction depends on them. Document hardware-dependent installation separately where needed; do not force one CUDA build on every machine.
- Use concrete integrity checks where available, such as checksums, expected class counts, schema checks, or a small loader/visual inspection. A folder's existence alone is not a data check.

## Research knowledge

`Idea/YYYY-MM-DD_<topic>.md` can separate existing evidence, unsupported conclusions, a falsifiable hypothesis, proposed experiments/ablations, and risks. Do not create this file for every coding task.

When process knowledge warrants preservation, separate current implementation explanations, stage completion status, and historical investigations. Promote verified reusable conclusions into stable guides as appropriate; do not paste whole conversations into README or treat an untested idea as an implemented feature.

These directories and names are optional conventions. Private notes may stay local; useful shared research notes may be deliberately versioned according to the project's policy.

## Git boundaries

Ordinary Git should retain the reproducible skeleton: code, configs, guides, dependency declarations, and small protocol metadata. Large datasets, archives, checkpoints, generated runs, environments, and caches are normally excluded. Existing DVC/LFS, artifact storage, or curated published results can justify a different boundary.

Use `.gitignore` for shared exclusions and `.git/info/exclude` for clone-local preferences. Do not assume a local rule will protect another clone. Do not overwrite existing rules or ignore small required metadata under a broad asset pattern.

When checking changed boundaries, use representative paths with `git check-ignore -v -- <path>` and inspect tracked assets with `git ls-files -- <path>`. An ignored file already in the index remains tracked. Report that case; removing it from tracking or rewriting history is a separate scoped operation.

If Git-sync instructions are part of the deliverable, show status/diff inspection and explicit intended paths for `git add --dry-run -- <paths>` rather than a blanket staging command. A layout change itself requires neither a commit nor a push.

## Source and adaptation boundary

These patterns were distilled from the supplied `PROJECT_FILE_ARCHITECTURE_REVIEW.md`, a review of the VLM_Clip local workspace on 2026-11-06. This skill is self-contained and does not require that source file at runtime. Its dataset names, algorithm parameters, exact file counts, empty placeholders, unimplemented package entrypoint, and local Git state are not template requirements.
