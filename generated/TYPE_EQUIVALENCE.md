# Survey Type Equivalence Matrix

**Generated from:** `survey-types.jsonld`  
**Last updated:** (auto-generated)

This document shows how question types map across different formats in the CDL survey ecosystem.

## Quick Reference Table

| XLSForm | LimeSurvey | DDI | Round-trip Safe | Data Structure | Key Warnings |
|---------|------------|-----|-----------------|----------------|--------------|
| `integer` | `N` | `var[@intrvl='contin']` | ✅ | single-column | — |
| `decimal` | `N` | `var[@intrvl='contin']` | ✅ | single-column | — |
| `text` | `S` | `var[@intrvl='discrete']` | ✅ | single-column | — |
| `note` | `X` | `var[@intrvl='discrete']` | ✅ | none | Note questions don't collect data but are preserved in DDI |
| `date` | `D` | `var[@intrvl='discrete']` | ✅ | single-column | — |
| `time` | `D` | `var[@intrvl='discrete']` | ✅ | single-column | LimeSurvey type D stores combined date+time; time-only granularity may be lost |
| `datetime` | `D` | `var[@intrvl='discrete']` | ✅ | single-column | — |
| `select_one` | `L` | `var[@intrvl='discrete']` | ✅ | single-column | Choice code truncation can cause ambiguity if two codes share 5-char prefix |
| `select_multiple` | `M` | `varGrp[@type='multipleResp']` | ⚠️ | multiple-binary-columns | Data structure fundamentally changes during transformation |
| `rank` | `R` | `var[@intrvl='discrete']` | ✅ | single-column | — |
| `calculate` | `*` | `var[@intrvl='discrete']` | ✅ | single-column | XPath expressions transpiled to ExpressionScript may not be fully equivalent |
| `geopoint` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | Not supported by LimeSurvey TSV import; xlsform2lstsv raises error |
| `geotrace` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | Not supported by LimeSurvey TSV import |
| `geoshape` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | Not supported by LimeSurvey TSV import |
| `start-geopoint` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | Background geolocation; not supported by LimeSurvey |
| `image` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | Media uploads not supported by LimeSurvey TSV import |
| `audio` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | Media uploads not supported by LimeSurvey TSV import |
| `video` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | Media uploads not supported by LimeSurvey TSV import |
| `file` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | File uploads not supported by LimeSurvey TSV import |
| `background-audio` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | Not supported by LimeSurvey TSV import |
| `barcode` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | Not supported by LimeSurvey TSV import |
| `phonenumber` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | Not supported by LimeSurvey TSV import; use text with constraint regex |
| `email` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | Not supported by LimeSurvey TSV import; use text with constraint regex |
| `csv-external` | `None` | `var[@intrvl='']` | ⚠️ | unsupported | External CSV loading not supported by LimeSurvey TSV import |
| `range` | `None` | `var[@intrvl='contin']` | ⚠️ | unsupported | Range/slider questions not supported by LimeSurvey TSV import |
| `acknowledge` | `None` | `var[@intrvl='discrete']` | ⚠️ | unsupported | Acknowledge type not supported by LimeSurvey TSV import |
| `select_one_from_file` | `None` | `var[@intrvl='discrete']` | ⚠️ | unsupported | External file choice lists not supported by LimeSurvey TSV import |
| `select_multiple_from_file` | `None` | `var[@intrvl='discrete']` | ⚠️ | unsupported | External file choice lists not supported by LimeSurvey TSV import |

## Detailed Type Information

### Acknowledge (`acknowledge`)

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
- ⚠️ Acknowledge type not supported by LimeSurvey TSV import

---

### Audio Recording (`audio`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Media uploads not supported by LimeSurvey TSV import

---

### Background Audio Recording (`background-audio`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Not supported by LimeSurvey TSV import

---

### Barcode Scanner (`barcode`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Not supported by LimeSurvey TSV import

---

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

### External CSV Reference (`csv-external`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ External CSV loading not supported by LimeSurvey TSV import

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

### Email Address (`email`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Not supported by LimeSurvey TSV import; use text with constraint regex

---

### File Upload (`file`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ File uploads not supported by LimeSurvey TSV import

---

### Geopoint (Latitude/Longitude) (`geopoint`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Not supported by LimeSurvey TSV import; xlsform2lstsv raises error

---

### Geoshape (Polygon) (`geoshape`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Not supported by LimeSurvey TSV import

---

### Geotrace (Line) (`geotrace`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Not supported by LimeSurvey TSV import

---

### Image Upload (`image`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Media uploads not supported by LimeSurvey TSV import

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
- **DDI:** `intrvl="discrete"`, `formatType="character"`

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

### Phone Number (`phonenumber`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Not supported by LimeSurvey TSV import; use text with constraint regex

---

### Range (Slider) (`range`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl="contin"`, `formatType="numeric"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Range/slider questions not supported by LimeSurvey TSV import

---

### Rank Order (`rank`)

**Platform Mappings:**
- **LimeSurvey:** Type `R`
  - Answer class: `A`
  - Supports 'other' option: ✅
- **DDI:** `intrvl="discrete"`, `formatType="numeric"`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`
- Choice codes: max 5 chars, pattern ``

**Transformation:**
- Round-trip safe: ✅ Yes
- Lossless: ✅ Yes
- Data columns: 1
- Data structure: single-column

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

### Start Geopoint (`start-geopoint`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Background geolocation; not supported by LimeSurvey

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

### Video Recording (`video`)

**Platform Mappings:**
- **LimeSurvey:** Type `None`
- **DDI:** `intrvl=""`, `formatType=""`

**Constraints:**
- Variable name: max 20 chars, pattern `^[a-zA-Z0-9]+$`

**Transformation:**
- Round-trip safe: ⚠️ No
- Lossless: ⚠️ No
- Data columns: 0
- Data structure: unsupported

**Warnings:**
- ⚠️ Media uploads not supported by LimeSurvey TSV import

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
