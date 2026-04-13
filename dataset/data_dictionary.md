# Data Dictionary

## Overview
This document describes the variables in `combined_experimental_data.csv` (N = 62).

## File Manifest
- `experimental_sample.csv` — First 5 rows of the experimental group (N = 41)
- `control_sample.csv` — First 5 rows of the control group (N = 21)
- `data_dictionary.md` — This file

## Variable Descriptions

| Variable | Type | Description | Range / Units |
|----------|------|-------------|---------------|
| `Student_ID` | String | Unique anonymous identifier (e.g., EXP_001, CTRL_001) | — |
| `Programming_Level` | Categorical | Baseline proficiency: `高级` (A), `中级` (B), `初级` (C) | A, B, C |
| `ComprehensiveMastery_Score` | Float | Eq. (7): Composite mastery index combining accuracy and dimensional sub-scores | [0, 1] |
| `Comprehensive_Learning_Behaviors_Score` | Float | Eq. (8): Composite learning-behavior index | [0, 1] |
| `Post_test_Score` | Float | Final learning outcome (post-intervention test) | 0–100 |
| `Daily_Study_Time` | Float | Average daily study time logged by the platform | Hours |
| `Problem_Attempts` | Float | Average number of attempts per problem | Count |
| `Knowledge_Transfer_Rate` | Float | Success rate on transfer tasks (novel problems) | Percentage (%) |
| `Learning_Satisfaction` | Float | Self-reported learning satisfaction | 1–5 Likert |
| `System_Usage_Frequency` | Float | Platform login/session frequency | Sessions / week |
| `Accuracy_Rate` | Float | Proportion of correctly answered questions | [0, 1] |
| `Concept_Understanding` | Float | Assessed concept-understanding dimension | [0, 1] |
| `Problem_Solving` | Float | Assessed problem-solving dimension | [0, 1] |
| `Code_Implementation` | Float | Assessed code-implementation dimension | [0, 1] |
| `Learning_Attitude` | Float | Assessed learning-attitude dimension | [0, 1] |
| `Independent_Solutions_Rate` | Float | Proportion of problems solved without hints | [0, 1] |
| `Active_Learning_Score` | Float | Index of active engagement behaviors | [0, 1] |
| `Learning_Persistence` | Float | Index of persistence across challenging items | [0, 1] |
| `Group` | Categorical | Experimental condition | Experimental, Control |

## Computed Variables

### `ComprehensiveMastery_Score` (Eq. 7)
Computed by `scoring_engine.py::comprehensive_mastery_score` as a weighted average of:
- `Accuracy_Rate` (w = 0.30)
- `Concept_Understanding` (w = 0.25)
- `Problem_Solving` (w = 0.25)
- `Code_Implementation` (w = 0.20)

All weights sum to 1.0 and the result is clipped to [0, 1].

### `Comprehensive_Learning_Behaviors_Score` (Eq. 8)
Computed by `scoring_engine.py::comprehensive_learning_behaviors_score` as:
```
0.60 · weighted_behavior_dims
+ 0.20 · min(1, Daily_Study_Time / 2.5)
+ 0.20 · min(1, Problem_Attempts / 3.5)
```
Clipped to [0, 1].

### `Programming_Level` Encoding
| Label | Meaning | English equivalent |
|-------|---------|-------------------|
| `高级` | Advanced | A-level (Proficient) |
| `中级` | Intermediate | B-level |
| `初级` | Beginner | C-level (Needs Improvement) |

## Usage Notes
- The dataset contains no personally identifiable information (PII).
- Full data and source code are available in the repository.
