---
name: paper-reading
description: Read attached English research papers and produce an evidence-grounded Chinese explanation for readers who know basic machine learning but not the paper's domain. Use when the user asks for a full paper summary, method walkthrough, experiment audit, or limitations analysis; do not use for an abstract-only paraphrase or a bibliography-only task.
---

# English Paper Reading

Use this skill to turn an English research paper into a Chinese explanation that lets the reader understand what the paper does, why it was proposed, how it is implemented, and whether the experiments support the claims.

## Core standard: evidence before fluency

- Read the paper that is actually available. Prefer the complete PDF, including method, experiments, appendix, supplementary material, tables, figures, and captions when present. Do not treat an abstract or a search snippet as the paper.
- If the full paper is unavailable or pages are unreadable, state the coverage and request the missing file when it is needed for a full audit. Any interim summary must be labeled as partial.
- Keep the paper's terminology and method names in English when that prevents ambiguity. Explain a technical term in Chinese the first time it appears.
- Separate these statements explicitly:
  - `论文明确陈述` — stated by the authors;
  - `实验直接支持` — supported by a reported comparison, ablation, analysis, or visualization;
  - `作者推测` — a hypothesis or interpretation presented by the authors without direct proof;
  - `基于实验的合理推断` — a cautious inference made from the reported evidence;
  - `未报告/无法核实` — information that the paper or the available file does not provide.
- Attach a locator to important claims and numbers whenever possible: section, equation, figure, table, appendix, or PDF page, for example `（见 Sec. 3.2、Eq. (4)、Table 2）`. Do not invent a locator.
- Never silently complete a missing equation, implementation detail, hyperparameter, dataset split, or statistical test. State what is visible and what is missing. If OCR makes a symbol uncertain, mark it as uncertain and verify it against surrounding text or the rendered page.
- Do not turn related work into a contribution of this paper. Distinguish `本文提出/采用/比较` and list only claims that the paper itself attributes to its contribution.

## Reading workflow

1. **Inventory the source.** Record title, venue/year if available, task, domain, paper type (method, analysis, theory, benchmark, or survey), and which sections or pages are inaccessible. Note whether the file is text-based or scanned.
2. **Build a claim map.** For each central claim, record the claim, its evidence location, evidence status, and the strongest caveat. This prevents abstract-level summaries from replacing the actual results.
3. **Reconstruct the problem.** Identify the input, output, training signal, evaluation protocol, source/target domains if applicable, label assumptions, and what existing bottleneck motivates the work.
4. **Reconstruct the method.** Follow the data from input to output. Transcribe only equations that appear in the paper, define every symbol, state the optimization target, and connect each loss or module to the problem it addresses. Keep training and inference separate.
5. **Audit the experiments.** Extract datasets, scale, splits, domains/classes, model and training settings, metrics and their direction, baselines, seeds or standard deviations, ablations, oracle/upper-bound settings, and qualitative results. Check whether the comparison is fair and whether the reported experiment tests the stated hypothesis.
6. **Test the conclusion boundary.** Compare each conclusion with its evidence. Identify assumptions, failure cases, computational cost, sensitivity, missing controls, and what the experimental coverage cannot establish.
7. **Write in the required structure below.** Put uncertainty next to the affected statement rather than hiding it in a generic disclaimer.

## Method reconstruction rules

When describing `A - Action`, include the following if the paper reports them:

- problem notation and the meaning of each input, output, label, domain, and parameter;
- model components and the order in which data passes through them;
- training objective, each loss term, optimization target, and how the terms are combined;
- data preprocessing, sampling, augmentation, pseudo-labeling, memory/update rules, or other non-obvious steps;
- inference-time inputs, outputs, post-processing, and any difference from training;
- which module addresses which bottleneck and how the modules interact.

Use the exact equation number when available. Explain an equation in words after displaying it, but do not derive a formula the paper does not give. If an implementation detail is inferred from a diagram or pseudocode, label it as an inference and cite that source.

## Experiment and number rules

- Report the actual method, strongest baseline, ablation variants, oracle/theoretical upper bound, and qualitative visualization separately. Do not merge them into one “best result.”
- Preserve the paper's units, rounding, split, and metric definition. Say whether a metric is higher-is-better or lower-is-better.
- Compute a relative improvement only when the compared values use the same setting and the denominator is meaningful. For a higher-is-better metric use `(method - baseline) / |baseline|`; for a lower-is-better metric use `(baseline - method) / |baseline|`. Label the value `按表中数值计算`, retain the paper's reported value separately, and avoid calculating when the paper gives incomparable averages or missing denominators. For percentages, distinguish percentage-point differences from relative percentage changes.
- Treat mean ± standard deviation, confidence intervals, and single-run numbers differently. Do not claim statistical significance unless the paper provides an appropriate statistical test.
- If two locations in the paper disagree, show both values and locations, say whether the difference may be rounding or a real inconsistency, and do not silently choose one.
- If the paper omits a requested item, write `未报告` or `不适用`; do not fill it from common practice or another paper.

## Required response structure

Answer in Chinese using the following headings. Keep the order unless the user explicitly asks for a different format.

### 1. 一句话核心结论

In one sentence state the research problem, core method, and main result. Include a locator if the sentence contains a precise number.

### 2. STAR 总结

#### S - Situation

Briefly explain the background, task definition, inputs/outputs, and only the domain terms needed to understand the paper. Assume the reader knows basic machine learning but not this domain. Avoid unrelated history.

#### T - Task

State the specific problem, the bottleneck in existing approaches, the paper's assumptions, and what success would mean. Separate the authors' stated motivation from your interpretation.

#### A - Action

Walk through the complete method and data flow. Preserve core equations in LaTeX, define symbols, explain each objective and module, and distinguish training from inference. Explicitly mark details as `未报告` or `基于图/伪代码的推断` when necessary.

#### R - Result

Use separate subsections for:

- actual method results;
- strongest baseline;
- ablation results and what each ablation tests;
- oracle or theoretical upper-bound results;
- qualitative visualization or case-study results.

For every important number give the table/figure/section locator and identify whether it is a mean, standard deviation, interval, or single run.

### 3. 独立实验总结

Use tables rather than burying settings in prose. At minimum include:

1. an experiment setup table with task, dataset and scale, source/target domains and class split when relevant, model/training settings, metric direction, and baselines;
2. a results table with the paper's main results, standard deviations or intervals, comparable relative improvement when it can be calculated, and the locator;
3. an ablation table with the removed/changed component, result, and the conclusion it can or cannot support.

For tasks without domains, class splits, or ablations, write `不适用` or `未报告`. Keep oracle, upper-bound, and qualitative rows visibly separate from ordinary baseline rows.

### 4. 论文的观察、假设和推导链

Present a chain with explicit labels:

`作者直接观察到的现象 → 提出的假设 → 假设如何变成算法或损失 → 哪个实验验证它 → 验证强度与剩余替代解释`

Use `作者推测` when the paper proposes an interpretation without directly isolating it experimentally. An ablation may show that a component helps, but it does not automatically prove the author's entire causal explanation.

### 5. 局限性与结论边界

Separate:

- limitations explicitly acknowledged by the paper;
- risks reasonably inferred from the experiments.

Discuss dependence on assumptions, likely failure scenarios, compute/data cost, hyperparameter or seed sensitivity, missing baselines/controls, and the breadth of datasets, domains, and metrics. Tie each point to evidence or label it as an inference.

### 6. 适合复述的精简版本

Write one coherent paragraph covering the background, core idea, method, and result. Keep the method name and the most defensible result, and do not overclaim beyond the evidence.

## Final quality check

Before finishing, verify that:

- the one-sentence conclusion agrees with the detailed results;
- every first-use technical term is briefly explained;
- contribution, related work, baseline, ablation, oracle, and visualization are not conflated;
- equations and symbols came from the paper or are clearly marked as inference;
- key numbers have a source locator, metric direction, and uncertainty information;
- the experiment table answers the requested fields or explicitly says `未报告/不适用`;
- claims are tagged when they are author speculation, reasonable inference, or direct experimental support;
- discrepancies across sections are called out;
- the limitations section states what the experiments cannot establish.
