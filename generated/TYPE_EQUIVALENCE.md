# Survey Type Equivalence Matrix

**Generated from:** `survey-types.jsonld`  
**Last updated:** (auto-generated)

This document shows how question types map across different formats in the CDL survey ecosystem.

## Quick Reference Table

| XLSForm | LimeSurvey | DDI | Round-trip Safe | Data Structure | Key Warnings |
|---------|------------|-----|-----------------|----------------|--------------|
| `decimal` | `N` | `var[@intrvl='contin']` | ✅ | single-column | — |
| `note` | `X` | `var[@intrvl='']` | ✅ | none | Note questions don't collect data but are preserved in DDI |
| `time` | `D` | `var[@intrvl='discrete']` | ✅ | single-column | LimeSurvey type D stores combined date+time; time-only granularity may be lost |
| `datetime` | `D` | `var[@intrvl='discrete']` | ✅ | single-column | — |
| `calculate` | `*` | `var[@intrvl='discrete']` | ✅ | single-column | XPath expressions transpiled to ExpressionScript may not be fully equivalent |
| `select_one_from_file` | `None` | `var[@intrvl='discrete']` | ⚠️ | unsupported | External file choice lists not supported by LimeSurvey TSV import |
| `select_multiple_from_file` | `None` | `var[@intrvl='discrete']` | ⚠️ | unsupported | External file choice lists not supported by LimeSurvey TSV import |
| `date` | `D` | `var[@intrvl='discrete']` | ✅ | single-column | — |
| `integer` | `N` | `var[@intrvl='contin']` | ✅ | single-column | — |
| `select_multiple` | `M` | `varGrp[@type='multipleResp']` | ⚠️ | multiple-binary-columns | Data structure fundamentally changes during transformation |
| `select_one` | `L` | `var[@intrvl='discrete']` | ✅ | single-column | Choice code truncation can cause ambiguity if two codes share 5-char prefix |
| `text` | `S` | `var[@intrvl='discrete']` | ✅ | single-column | — |

## Detailed Type Information

### Calculated Field (`calculate`)

**Platform Mappings:**
- **LimeSurvey:** Type `*`
- **DDI:** `intrvl="discrete"`, `formatType="character"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ✅ Yes
- Lossless: ⚠️ No
- Data columns: 1
- Data structure: single-column

**Warnings:**
- ⚠️ XPath expressions transpiled to ExpressionScript may not be fully equivalent

---

### Date (`date`)

**Platform Mappings:**
- **LimeSurvey:** Type `D`
- **DDI:** `intrvl="discrete"`, `formatType="character"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ✅ Yes
- Lossless: ✅ Yes
- Data columns: 1
- Data structure: single-column

---

### Date+Time (`datetime`)

**Platform Mappings:**
- **LimeSurvey:** Type `D`
- **DDI:** `intrvl="discrete"`, `formatType="character"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ✅ Yes
- Lossless: ✅ Yes
- Data columns: 1
- Data structure: single-column

---

### Decimal/Float (`decimal`)

**Platform Mappings:**
- **LimeSurvey:** Type `N`
- **DDI:** `intrvl="contin"`, `formatType="numeric"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ✅ Yes
- Lossless: ✅ Yes
- Data columns: 1
- Data structure: single-column

---

### Integer (`integer`)

**Aliases:** `int`

**Platform Mappings:**
- **LimeSurvey:** Type `N`
- **DDI:** `intrvl="contin"`, `formatType="numeric"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ✅ Yes
- Lossless: ✅ Yes
- Data columns: 1
- Data structure: single-column

---

### Note (Display Text) (`note`)

**Platform Mappings:**
- **LimeSurvey:** Type `X`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ✅ Yes
- Lossless: ✅ Yes
- Data columns: 0
- Data structure: none

**Warnings:**
- ⚠️ Note questions don't collect data but are preserved in DDI

---

### Multiple Choice (Checkboxes) (`select_multiple`)

**Platform Mappings:**
- **LimeSurvey:** Type `M`
  - Answer class: `SQ`
  - Supports 'other' option: ✅
- **DDI:** `intrvl="discrete"`, `formatType="numeric"`
  - Structure: `<varGrp type="multipleResp">` with binary-per-choice

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`
- Choice codes: max 5 chars, pattern `^[a-zA-Z0-9]+$`
- ⚠️ Choice codes > 5 chars will be truncated in LimeSurvey
- ⚠️ Avoid choice codes with identical 5-char prefixes

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: n-choices
- Data structure: multiple-binary-columns

**Structure Changes During Transformation:**
- XLSForm → DDI: Single question → varGrp with binary child variables
- Survey Data → DDI CSV: Space-separated values → separate binary columns

**Warnings:**
- ⚠️ Data structure fundamentally changes during transformation
- ⚠️ Original column contains space-separated codes; DDI exports n binary columns

---

### Select Multiple (from file) (`select_multiple_from_file`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl="discrete"`, `formatType="numeric"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ External file choice lists not supported by LimeSurvey TSV import

---

### Single Choice (Radio Buttons) (`select_one`)

**Platform Mappings:**
- **LimeSurvey:** Type `L`
  - Answer class: `A`
  - Supports 'other' option: ✅
- **DDI:** `intrvl="discrete"`, `formatType="numeric"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`
- Choice codes: max 5 chars, pattern `^[a-zA-Z0-9]+$`
- ⚠️ Choice codes > 5 chars will be truncated in LimeSurvey

**Transformation:**
- Round-trip safe: ✅ Yes
- Lossless: ✅ Yes
- Data columns: 1
- Data structure: single-column

**Warnings:**
- ⚠️ Choice code truncation can cause ambiguity if two codes share 5-char prefix

---

### Select One (from file) (`select_one_from_file`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl="discrete"`, `formatType="numeric"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ External file choice lists not supported by LimeSurvey TSV import

---

### Text (Short Free Text) (`text`)

**Aliases:** `string`

**Platform Mappings:**
- **LimeSurvey:** Type `S`
- **DDI:** `intrvl="discrete"`, `formatType="character"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ✅ Yes
- Lossless: ✅ Yes
- Data columns: 1
- Data structure: single-column

---

### Time (`time`)

**Platform Mappings:**
- **LimeSurvey:** Type `D`
- **DDI:** `intrvl="discrete"`, `formatType="character"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ✅ Yes
- Lossless: ✅ Yes
- Data columns: 1
- Data structure: single-column

**Warnings:**
- ⚠️ LimeSurvey type D stores combined date+time; time-only granularity may be lost

---

## Structural Types

These are not question types but affect survey structure:

### Group (Begin) (`begin_group`)

⚠️ **LimeSurvey does not support nested groups** (groups are flattened)

**DDI Preservation:** Conditional

- **If** appearance='table-list' OR name contains 'grid' OR label contains 'matrix'  
  **Then:** varGrp[@type='grid']
- **If** else  
  **Then:** DROPPED - variables flattened to top level

**Warnings:**
- ⚠️ Plain groups lost in XLSForm → DDI → XLSForm round trip
- ⚠️ Always use appearance='table-list' if group structure matters
- ⚠️ Nested groups flattened in LimeSurvey (not supported)

---

### Repeat Group (`begin_repeat`)

⛔ **Not supported in LimeSurvey**

**Warnings:**
- ⚠️ Repeat groups not supported in LimeSurvey or DDI export
- ⚠️ Variables inside begin_repeat/end_repeat are silently skipped
- ⚠️ Requires different data model (nested arrays) not currently implemented

---

### Group (End) (`end_group`)


---

### Repeat Group (End) (`end_repeat`)

⛔ **Not supported in LimeSurvey**

---
