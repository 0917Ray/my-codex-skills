# Step-by-step reproduction guides

Read whenever writing or revising project setup, preparation, execution, or replot instructions. A guide is an ordered command tutorial that a reader can follow from a new shell; a directory description or parameter table alone is insufficient.

## Command contract

For every step, state its goal, required environment/working directory, command, and observable success check. Explain which step supplies each input. Use fenced shell blocks without `$` prompts so commands are easy to copy. Put alternative branches in separately labeled blocks; a reader should not execute mutually exclusive installation or experiment variants in sequence by accident.

Use real entrypoints, existing config files, actual parser options, and supported combinations. Inspect `--help` or parser definitions, config loaders, and dependency declarations before documenting them. Check what a CLI override changes and whether it supports lists. Do not invent `--seeds`, `--device`, `--resume`, `--no-plot`, or a download helper simply because they would be convenient. If implementing the workflow is in scope, add the needed interface and then document it; if only writing documentation, describe missing functionality explicitly.

Resolve project-specific names, versions, paths, URLs, and values in the delivered guide. If a user must supply a private path, token, or gated dataset, identify it before the command and explain how to obtain/provide it. Never label placeholder commands as ready to run. Do not log credentials. Distinguish observed output from expected output and record checks not run due to missing data/hardware.

## 1. Establish the starting point

State the supported OS/shell, Conda prerequisite, compute/storage requirements, and relevant CPU/GPU limitations. Show how to obtain the project when that is part of the task, enter its root, and confirm the working directory. Use the real clone URL/revision if known. Otherwise start from the provided local repository and explain that starting assumption.

Subsequent sections should state that commands run from that root in the named environment, and explicitly mark any exception. A fresh shell must reactivate the environment and return to the root; do not depend on invisible shell state.

## 2. Create and verify the Conda environment

Use Conda exclusively for environment creation/management. Do not propose `venv`, virtualenv, Poetry/uv-managed environments, or system Python as alternatives. If `conda` is absent, explain how to install an appropriate Conda distribution for the user's OS/architecture using its authoritative source; do not silently change environment managers or install software merely because writing the guide requires describing it.

Prefer an actual maintained `environment.yaml` in a new project. Its name, Python version, channels, dependencies, and any pip section must agree with the implementation and target platform. For an existing repository, a documented `conda create` followed by installation from existing dependency declarations is also valid. Choose one canonical setup path and make hardware-specific branches explicit.

For example, **only if the project's file really defines `name: research-project`**, a guide can use:

```bash
conda --version
conda env create -f environment.yaml
conda activate research-project
python -c "import sys; print(sys.executable); print(sys.version)"
conda env list
```

Explain that the executable and active environment should point to `research-project`, not `base` or system Python. If activation fails, give shell-appropriate Conda initialization instructions and note when a new shell is required. Do not blindly recreate an existing environment: explain how to activate it and, if dependencies changed, update it using the actual maintained declaration. Avoid destructive environment removal as a routine setup step.

If using `conda create`, specify a Python version supported by the code/dependencies rather than automatically choosing the newest version. Install suitable Conda dependencies first. When pip is needed for project dependencies, run `python -m pip` only after activation (or through `conda run -n <actual-name>`). Use the actual `requirements.txt`, package installation, or pip section; do not install the same dependency twice through conflicting instructions. Never install into `base` or system Python.

For GPU projects, explain driver/framework compatibility and give the applicable pinned installation route and device verification command. Separate CPU and GPU choices when both are supported; do not assume CUDA on macOS or an NVIDIA GPU on every machine. Verify imports of the actual required packages and device availability after installation. If GPU-only computation cannot run on the current machine, state that boundary clearly.

## 3. Prepare every required dataset and checkpoint

For each input, give the following in executable order:

1. Source, version/split, license/access requirements where relevant, expected download size, and whether it is required or optional.
2. Actual download command or explicit manual acquisition procedure when authentication/terms prevent an automated download. Name the local destination and create its parent directory.
3. Checksum/archive integrity check where available and an archive-content inspection command before extraction. Explain an extra top-level archive directory using the actual archive layout; do not blindly move or overwrite existing data.
4. Extraction/preparation commands and the final expected directory tree, retaining upstream IDs. Include generated label/split metadata and the actual preparation helper if one exists.
5. A concrete check: expected counts/checksums/schema, a bounded loader check, or a small visualization with a known output. State what success looks like; a directory merely existing is insufficient.
6. The exact YAML keys or supported CLI options that point the experiment to the prepared paths. Explain the path base and how to select external storage without relocating large datasets unnecessarily.

Give equivalent source/download/location/verification instructions for checkpoints when required. Explain mapping between logical model names and checkpoint filenames. Do not make optional datasets or a costly full corpus mandatory for a workflow that does not need them. If inputs are unavailable, describe the missing prerequisite rather than inventing verification results.

## 4. Verify the installation and run a smoke test

First show the actual entrypoint's help/import/config validation check where available. Then give a bounded small-run command with limited samples/steps, few workers/devices, and a temporary output distinct from formal results. State the specific config/overrides that reduce cost and how to recognize completion.

Identify expected logs and result files and give inspection commands appropriate to the actual format. Warn next to the command that reduced-input metrics are execution checks, not formal reported results. A small run and the full run should share the same implementation.

## 5. Run formal experiments and select configurations

For each implemented workflow, provide its own explicit command and explain when to use it. Cover baseline, standard method, quick check, parameter sweep, or other modes only when they exist. A config filename in a table alone is not an execution tutorial.

This is an **illustrative command pattern**, not a verified project CLI. Replace script names/options with the implemented interface when producing a guide:

```bash
python scripts/evaluate_method.py --config configs/evaluation/baseline.yaml
```

For the same illustrative interface, a separate sweep choice would be:

```bash
python scripts/evaluate_method.py --config configs/evaluation/method_sweep.yaml
```

In the delivered guide, explain which command is an alternative, which config values differ, and the expected output family. Add a compact comparison table if helpful: purpose, config, seed/sample scope, output, and approximate cost only when known. Commands must use actual config paths and avoid overlapping output destinations.

Show how to edit relevant YAML fields and how to use supported one-off CLI overrides, such as changing device, data root, worker count, or output directory. Explain precedence and that overrides do not rewrite the baseline file. Use a real override command; do not infer a flag from the name of a config key. State parameter units and whether workers/resources are per task or global.

For multi-seed experiments, show the actual YAML seed list, the single command that runs it in order, and the per-seed and final summary paths. Explain independent initialization and the mean/std definition, expected/completed seed counts, partial-failure behavior, and `.md`/`.json`/`.csv` exports. Show existing resume/aggregation-only commands only when supported.

## 6. Inspect results and redraw figures

Show the actual output hierarchy and commands to inspect at least one machine-readable result, the Markdown summary, and the run log. Explain run/variant/seed identity, sample scope, metrics/units, and aggregation. Include the meaning of progress/status messages and how to find non-actionable warnings in the file log. Distinguish incomplete runs from completed results.

State that plots normally appear automatically after successful training/evaluation and result aggregation. Identify the saved chart-ready data, plotting config, script, and images. Give a standalone redraw command for that exact bundle or implemented plotting entrypoint; explain its working directory, Conda environment, input-path base, and output destination.

Demonstrate changing actual plot fields (for example colors, labels, figure size, or series selection), then running the redraw command without training/evaluation. Explain how to target a real execution directory rather than an assumed latest run, and whether redraw overwrites images or uses a fresh destination. If automatic plotting fails, preserve computation outputs and show how to retry only plotting.

## 7. Troubleshoot and validate the guide

Use concrete problem → check → fix entries for issues the workflow actually encounters: wrong environment/interpreter, missing data or checkpoint, archive nesting, unsupported device, invalid config field, incorrect path base, and incomplete/failed seeds. Link a shared preparation guide instead of repeating installation steps in every experiment guide; each workflow must still tell the reader exactly where to start and what to do next.

Before delivery, walk the commands in order from the documented starting state. Validate supported flags, config values/paths, file links, and expected output names. Run inexpensive checks in the project's Conda environment when available; do not start downloads, full training, or expensive evaluation solely to validate documentation. Report what was actually executed, what was checked statically, and what depends on unavailable data, Conda, hardware, or access. A plausible command sequence is not evidence that it has succeeded.
