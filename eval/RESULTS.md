# Evaluation results

Small hand-written sets (see the JSON files). These numbers demonstrate the method on
a limited, partly self-authored test set; they are not a claim of general accuracy.

## 1. Skill extraction (22 labeled snippets, dictionary skills only)

- Precision: **0.98**
- Recall: **0.98**
- F1: **0.98**

Mismatches:

- "I will go to the gym and then react quickly to alerts"  extra: ['React']  missed: -  (known false positive: 'react' as a verb)
- "Built REST endpoints for a ticketing system"  extra: -  missed: ['REST APIs']  (known miss: phrase not in the alias list)

## 2. Score ranking

For every job description, each pair of resumes with different human fit labels should be
ordered correctly (higher label gets a strictly higher score). Ties count as failures.

| Method | Correct pairs | Ties | Accuracy |
|---|---|---|---|
| keyword only | 41/47 | 1 | 87% |
| keyword + related | 44/47 | 0 | 94% |
| text similarity only | 44/47 | 2 | 94% |
| blend (70% keyword+related / 30% similarity) | 44/47 | 0 | 94% |

Misordered pairs (keyword + related):

- backend: G_paraphrased_backend (label 2, 25%) vs C_data (label 0, 33%)
- backend: G_paraphrased_backend (label 2, 25%) vs D_fullstack (label 1, 42%)
- backend: G_paraphrased_backend (label 2, 25%) vs E_related_stack (label 1, 46%)

### Scores by resume and job (keyword + related)

| Resume | backend | frontend | data | fullstack |
|---|---|---|---|---|
| A_backend_java | 83% (label 2) | 17% (label 0) | 7% (label 0) | 31% (label 0) |
| B_frontend | 17% (label 0) | 100% (label 2) | 0% (label 0) | 50% (label 1) |
| C_data | 33% (label 0) | 17% (label 0) | 86% (label 2) | 31% (label 0) |
| D_fullstack | 42% (label 1) | 50% (label 1) | 21% (label 0) | 94% (label 2) |
| E_related_stack | 46% (label 1) | 8% (label 0) | 11% (label 0) | 44% (label 1) |
| F_irrelevant | 0% (label 0) | 0% (label 0) | 0% (label 0) | 0% (label 0) |
| G_paraphrased_backend | 25% (label 2) | 8% (label 0) | 0% (label 0) | 19% (label 0) |
