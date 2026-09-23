# Data quality report

All percentages are records affected divided by raw/clean opportunity rows; classes overlap.

```text
                check  affected_records  total_records  percentage phase
   missing_key_fields              2012         201200    1.000000   raw
duplicate_opportunity              1200         201200    0.596421   raw
       invalid_record              3015         201200    1.498509   raw
       amount_outlier              1002         201200    0.498012   raw
   date_inconsistency              2971         201200    1.476640   raw
     missing_industry              1005         201200    0.499503   raw
          missing_rep              1007         201200    0.500497   raw
   missing_key_fields                 0         198000    0.000000 clean
duplicate_opportunity                 0         198000    0.000000 clean
       invalid_record                 0         198000    0.000000 clean
       amount_outlier                 0         198000    0.000000 clean
   date_inconsistency                 0         198000    0.000000 clean
     missing_industry                 0         198000    0.000000 clean
          missing_rep                 0         198000    0.000000 clean
```

Raw opportunities: 201,200. Clean: 198,000. Quarantined: 2,000. Customer duplicate rows removed: 167.

Duplicate IDs retain the first occurrence (injected duplicates are exact). Customer master restores geography and industry; account ownership restores missing representatives. Stage-event evidence restores chronology and stage/status. Financial identities are recomputed. Invalid gross amounts/discounts are quarantined, never invented. Dependent fact rows are excluded consistently. Optional nulls (open close dates, missing future actions) remain legitimate. Source provenance is defined in docs/METHODOLOGY.md.
