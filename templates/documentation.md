# Technical Documentation

This document describes the core classes and functions used to extract data from an EPPI-Reviewer JSON export. These underpin every extraction option in the web application.

---

## Overview

The extraction pipeline has five classes, each with a distinct role:

| Class | Role |
|---|---|
| `JSONDataExtractor` | Loads the JSON file and provides all low-level data retrieval methods |
| `DataFrameCompilation` | Builds the standard numbered DataFrames (1–8, 10–11) |
| `StrandSpecificFrames` | Builds strand-specific DataFrames (option 6) |
| `RiskofBias` | Computes padlock scores (option 9) |
| `CustomFrames` | Builds DataFrames from a user-selected subset of columns |

A typical extraction follows this pattern:

```python
extractor = JSONDataExtractor("path/to/export.json")
dfc = DataFrameCompilation(extractor)
df = dfc.make_dataframe_1()
```

---

## JSONDataExtractor

The foundation class. Loads the JSON file on initialisation and exposes methods for reading every type of coded data.

### `__init__(data_file)`

Loads the JSON export into memory.

```python
extractor = JSONDataExtractor("eppi_export.json")
```

| Parameter | Type | Description |
|---|---|---|
| `data_file` | `str` | Path to the EPPI-Reviewer `.json` export file |

---

### Low-level retrieval methods

These are called internally by `retrieve_data`, `retrieve_info`, and `retrieve_ht`. You rarely need to call them directly.

---

#### `get_data(codes)`

Reads **coded attribute** data — questions where the coder selected one or more predefined answer options.

```python
data = extractor.get_data(pub_year_output)
```

| Parameter | Type | Description |
|---|---|---|
| `codes` | `list[dict]` | A list containing one attribute dict from `attributeIDs.py`, e.g. `[{5001: "RCT", 5002: "Quasi-experiment"}]` |

**Returns** a nested list: one entry per attribute dict, each containing one entry per study. Each study entry is a list of matched label strings, or `["NA"]` if no match was found.

**When to use:** attributes whose dict values are non-empty label strings — i.e. the answer is one of a fixed set of options.

---

#### `comments(codes)`

Reads **free-text / numeric input** fields — questions where the coder typed a value rather than selecting from options.

```python
data = extractor.comments(pp_incentive_amount_output)
```

Looks for `AdditionalText` on each matched attribute in the JSON. Returns `"NA"` for studies where the field was left blank.

**When to use:** attributes whose dict values are `""` (empty string) in `attributeIDs.py`.

---

#### `highlighted_text(codes)`

Reads **highlighted text** fields — passages of source text that the coder highlighted inside EPPI-Reviewer.

```python
data = extractor.highlighted_text(pub_type_output)
```

Looks for `ItemAttributeFullTextDetails` on each matched attribute. Returns `"NA"` if no text was highlighted.

---

#### `retrieve_metadata(var, col_name)`

Reads **top-level study metadata** fields that live directly on the reference object (not inside `Codes`).

```python
df = extractor.retrieve_metadata("Year", "pub_year")
df = extractor.retrieve_metadata("ShortTitle", "pub_author")
```

| Parameter | Type | Description |
|---|---|---|
| `var` | `str` | Field name on the JSON reference object, e.g. `"Year"`, `"ShortTitle"`, `"ItemId"` |
| `col_name` | `str` | Column name to use in the returned DataFrame |

**Returns** a single-column `pd.DataFrame` with one row per study.

---

### High-level retrieval methods

These wrap the low-level methods above, converting raw lists into tidy single-column DataFrames ready for concatenation.

---

#### `retrieve_data(id, col_name)`

Wraps `get_data()`. Use for coded-option attributes (non-empty label values).

```python
df = extractor.retrieve_data(study_design_output, "study_design")
```

| Parameter | Type | Description |
|---|---|---|
| `id` | `list[dict]` | Attribute dict from `attributeIDs.py` |
| `col_name` | `str` | Column name in the returned DataFrame |

**Returns** a single-column `pd.DataFrame`, one row per study.

---

#### `retrieve_info(id, col_name)`

Wraps `comments()`. Use for free-text / numeric input attributes (empty string `""` values in `attributeIDs.py`).

```python
df = extractor.retrieve_info(pp_incentive_amount_output, "pp_incent_amount")
```

Same signature as `retrieve_data`. If you use `retrieve_data` on a free-text field by mistake, every cell will be empty — use `retrieve_info` instead.

---

#### `retrieve_ht(id, col_name)`

Wraps `highlighted_text()`. Use to pull in the raw text passages highlighted by coders alongside a coded attribute.

```python
df = extractor.retrieve_ht(pub_type_output, "pubtype_ht")
```

Same signature as `retrieve_data`.

---

### Choosing the right retrieval method

| Attribute dict value | Correct method | Wrong method |
|---|---|---|
| Non-empty string e.g. `"RCT"` | `retrieve_data` | — |
| Empty string `""` | `retrieve_info` | `retrieve_data` (returns blanks) |
| Highlighted text needed | `retrieve_ht` | — |
| Top-level metadata (`"Year"` etc.) | `retrieve_metadata` | — |

---

### `clean_up(df)`

Static method applied automatically by all `retrieve_*` methods. Strips characters that break CSV output: `\r`, `\n`, `:`, `;` are each replaced with a space.

---

### Outcome-level methods

These handle data that is nested under individual outcomes rather than at study level.

| Method | Description |
|---|---|
| `get_outcome_lvl1(var)` | Reads a top-level outcome field (e.g. `"OutcomeText"`) across all outcomes for all studies |
| `get_outcome_lvl2(var)` | Reads a coded attribute from within `OutcomeCodes` — outcome-level equivalent of `get_data()` |

Both return nested lists aligned to the maximum outcome count across the dataset, padding with `"NA"` for studies with fewer outcomes.

---

## DataFrameCompilation

Builds the eight standard extraction DataFrames. Each method calls a set of `retrieve_*` calls, concatenates the results, fills missing values with `"NA"`, and returns a `pd.DataFrame`.

```python
dfc = DataFrameCompilation(extractor)
df1 = dfc.make_dataframe_1()
```

### Constructor

```python
DataFrameCompilation(data_extractor)
```

| Parameter | Type | Description |
|---|---|---|
| `data_extractor` | `JSONDataExtractor` | An initialised extractor instance |

### Methods

| Method | Option | Description |
|---|---|---|
| `make_dataframe_1(clean_cols=False)` | 1 | General study information |
| `make_dataframe_2(clean_cols=False)` | 2 | Participants & schools |
| `make_dataframe_3(clean_cols=False)` | 3 | Sample size |
| `make_dataframe_4(clean_cols=True)` | 4 | Effect size A |
| `make_dataframe_5(clean_cols=True)` | 5 | Effect size B |
| `make_dataframe_7(clean_cols=False)` | 7 | Other educational outcomes |
| `make_dataframe_8()` | 8 | Study security |
| `make_dataframe_10()` | 10 | References |

### `clean_cols` parameter

When `clean_cols=True`, each method inserts additional empty `_CLEAN` columns alongside data columns. These act as spacer columns for manual data checking and correction workflows (e.g. in Excel).

```python
df = dfc.make_dataframe_1(clean_cols=True)
# Columns include: id, pub_author, pub_year, pub_year_CLEAN, ...
```

Default is `True` for DataFrames 4 and 5, `False` for all others.

---

## StrandSpecificFrames

Builds the strand-specific DataFrame (option 6). Each strand has its own method returning only the columns relevant to that topic.

```python
ssf = StrandSpecificFrames(extractor)
df = ssf.strand_specific_df_selection(user_input)
```

### `strand_specific_df_selection(user_input)`

Dispatches to the correct strand method based on the integer strand key.

| Parameter | Type | Description |
|---|---|---|
| `user_input` | `int` | Strand key (1–32), matching the keys in `STRAND_OPTIONS` in `web_app.py` |

Returns a `pd.DataFrame` for the selected strand, or raises `NameError` if the key is out of range.

---

## RiskofBias

Computes padlock scores for each study.

```python
rob = RiskofBias(extractor)
rob.compile()
df, summary = rob.padlocks(save_file=False)
```

### `compile()`

Initialises all the raw risk-of-bias variables from the JSON. Must be called before `padlocks()`.

### `padlocks(save_file=True)`

Calculates the padlock score for each study. The score starts at 5 and one point is deducted for each of the five criteria rated `"H"` (High risk):

| Criterion | Deduction trigger |
|---|---|
| % Randomised | Rated H |
| % High Ecological Validity | Rated H |
| % Independent Evaluation | Rated H |
| % Published since 2000 | Rated H |
| Median % Attrition (reported) | Rated H |

Deductions are additive and the score is clamped to a minimum of 0.

| Parameter | Type | Description |
|---|---|---|
| `save_file` | `bool` | If `True`, writes a CSV to the working directory. Default `True`. Set `False` in the web app. |

**Returns** a tuple `(df, path)` where `df` is the padlock scores DataFrame and `path` is the output file path (or `None` if `save_file=False`).

---

## attributeIDs.py

All attribute ID mappings live in `eefdata/src/attributeIDs.py` and are imported wholesale into `funcs.py` via `from .attributeIDs import *`.

Each variable is a list containing a single dict that maps integer EPPI-Reviewer `AttributeId` values to human-readable label strings:

```python
# Coded-option field — values are label strings
study_design_output = [{
    5001: "Randomised Controlled Trial",
    5002: "Quasi-experiment",
    5003: "Regression discontinuity",
}]

# Free-text field — value is empty string; real data is in AdditionalText
pp_incentive_amount_output = [{
    8250007: "",
}]
```

The empty string `""` is the signal that `retrieve_info()` must be used instead of `retrieve_data()`.
