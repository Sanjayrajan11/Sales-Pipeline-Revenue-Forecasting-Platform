# Final validation record

Final audit: 2026-09-23. Scope: the existing Sales Pipeline & Revenue Forecasting Platform, preserved and hardened for a local educational portfolio. This is not a production security, load or accessibility certification.

## Executed evidence

| Check | Actual result |
| --- | --- |
| Clean Python installation | Python 3.12.14; isolated venv without inherited packages; requirements installation and pip check passed |
| Final pytest | 68 passed; 0 failed; 0 errors; 0 skipped; 62.59 seconds |
| Final pipeline | Reused existing raw data; completed in 43.37 seconds; 42 SQL statements executed |
| Raw-data preservation | SHA-256 unchanged for all 18 raw files |
| Chrome | Installed Google Chrome 153.0.8010.53; 55 recorded checks |
| Responsive coverage | All 12 workspaces at 1440 desktop, 1280, 820 and 390 pixels; chart data and bottom-of-page checks at 390 |
| Notebooks | All five executed successfully with no error outputs |
| Power BI export | Export utility executed; Desktop / .pbix execution is not claimed |
| Static checks | Ruff passed; repository links, excluded files and common credential/local-path patterns checked |

Evidence: [pytest XML](../reports/pytest-results.xml), [Chrome audit](../reports/browser_validation.json), [run manifest](../reports/run_manifest.json), [data realism audit](../reports/data_realism_audit.md), [environment record](../reports/validation_environment.json) and actual images in [screenshots](../screenshots). `reports/github_readiness.json` records the archive audit.

## Business calculations checked by hand

[Acceptance tests](../tests/test_handchecked.py) use nine illustrative deals, separate from the portfolio dataset. Values below are INR, not business results.

| Measure | Independently calculated expectation |
| --- | --- |
| Total / won / lost / active value | 1,900 / 400 / 500 / 1,000 |
| Weighted active pipeline | 400 |
| Resolved win rate | 2 / 3 |
| Average and median won deal | 200 each |
| Mean won cycle | (10 + 30) / 2 = 20 days |
| Stale active rate | 3 / 6 = 50% |
| Top-five active concentration | 950 / 1,000 = 95% |
| Quota attainment / remaining quota | 400 / 1,000 = 40%; remaining 600 |
| Face / weighted coverage | 1,000 / 600 and 400 / 600 |
| Stage conversion / dropout | One advance and one loss among two exits = 50% each; one pending excluded |
| Risk / health | 15 stale + 10 close pressure + 10 long cycle = 35; eight health components sum to 73.1 |
| Scenario | (400 + 1,000 × 0.1) × 1.1 × 0.95 = 522.5; gap 577.5 against adjusted 1,100 target |
| Revenue growth | 100 → 150 → 120 means +50%, then −20% |
| Forecast variance | Predictions 110, 140, 120 against actuals 100, 150, 120 give +10, −10, 0 |

Full-dataset KPIs also reconcile independently. Historical forecasts reconstruct creation, stage entry and resolution at each cutoff. Mutation tests prove that later stage/outcome changes do not alter an earlier snapshot. Model selection uses validation only; the test period follows it. Mid-month calendar alignment has a separate regression test.

## Final hardening

- Preserved the implementation, architecture, layout and saved dataset; subsequently applied the requested black background, white text and grayscale chart theme across all workspaces.
- Corrected chart-title clipping on phone widths by using wrapping text above charts.
- Rejected non-finite planning inputs and fractional opportunity counts/horizons.
- Aligned mid-month forecasts with the next complete month and seasonal offset.
- Made the generated model-selection explanation depend on the selected model.
- Declared PyArrow explicitly as the pipeline's Parquet dependency (Streamlit also depends on it).
- Added exact business examples, recovery checks and complete Chrome regression evidence.

Browser automation targets Streamlit's visible labels and grid event surface. Earlier automation failures came from styled input overlays and asynchronous reruns; the final run exercises actual user controls and validates resulting content/downloads. No force-click or DOM state mutation substitutes for a successful interaction.

The theme-update regression run used a fresh workspace-local pytest `--basetemp` directory because Windows denied access to the default shared temporary directory. No test was weakened or skipped.

## Quality gate

| Requirement | Status | Evidence / scope |
| --- | --- | --- |
| Dataset generated | VERIFIED | Saved 200,000-opportunity generation reused; deterministic generation tests pass. |
| Dataset realistic | VERIFIED | Amounts, stages, cycles, discounts, activity timing, quotas and group variation audited. |
| Data-quality issues handled | VERIFIED | 1,200 opportunity duplicates removed; 2,000 financial records quarantined; all clean quality checks zero. |
| Cleaning works | VERIFIED | Full pipeline and adversarial cleaning tests pass. |
| Database works | VERIFIED | Atomic publication and SQLite integrity_check pass. |
| SQL executes | VERIFIED | All 42 statements execute and reconcile. |
| KPI calculations verified | VERIFIED | Independent nine-deal examples and full-record reconciliation. |
| Pipeline analysis verified | VERIFIED | Inventory partitions, weighting, period-aligned coverage and concentration checked. |
| Funnel analysis verified | VERIFIED | Actual event exits, advances, losses and pending denominators reconciled. |
| Forecast generated | VERIFIED | Twelve complete future monthly periods published. |
| Forecast backtested | VERIFIED | Nine candidates; six validation and six held-out origins; selected WAPE independently recomputed. |
| Risk engine works | VERIFIED | Bounds, drivers, closed exclusions and an exact 35-point example pass. |
| Scenario planner works | VERIFIED | Hand-calculated sensitivity, input boundaries, live control and CSV checks pass. |
| Recommendations are dynamic | VERIFIED | Evidence and exposure reconcile to current filtered opportunity records. |
| Tests pass | VERIFIED | 68 passed; zero failures, errors or skips in the clean environment. |
| Streamlit launches | VERIFIED | Final application launched in the clean environment at localhost:8501. |
| Every page loads | VERIFIED | All 12 workspaces pass AppTest and real Chrome navigation. |
| Filters work | VERIFIED | Global region, local search, empty results and unallocated-quota behavior exercised. |
| Tables work | VERIFIED | Rendered data grids, ascending sort and complete-result export checked. |
| Downloads work | VERIFIED | Scenario CSV parsed; explorer export exceeds the 500-row display cap and respects sort. |
| Drill-down works | VERIFIED | Stage lane selection and actual opportunity row timeline verified in Chrome. |
| No traceback | VERIFIED | No unhandled app exception in final navigation; missing-data and invalid-ID recovery tested. |
| No placeholder content | VERIFIED | Source review, text scan and all-workspace inspection completed. |
| No hardcoded business results | VERIFIED | Displayed results derive from analytical records; report selection narrative is conditional. |
| README complete | VERIFIED | Business problem, setup, architecture, modules, results, limits and synthetic disclaimer present. |
| Documentation complete | VERIFIED | Required BA documents, dictionaries, 30 stories, 66 Q&As and Power BI guide reviewed. |
| GitHub structure clean | VERIFIED | Git-visible source archive excludes local runtime, raw/processed datasets, DB and caches; see github_readiness.json. |
| Browser validation completed | VERIFIED | 55 recorded real Chrome checks plus rendered-chart assertions. |
| Responsive layout checked | VERIFIED | All workspaces at 1280, 820 and 390 pixels; desktop at 1440; long titles wrap; no page-level horizontal overflow. |

## Explicit boundaries

GitHub upload is **not performed**; the deliverable is an audited upload-ready source archive. Power BI Desktop execution is **NOT VERIFIED** because the deliverable is a model/DAX guide, not a .pbix. Multi-user production deployment, authentication, load testing, exhaustive accessibility certification and real-world predictive performance are **NOT VERIFIED** and outside this portfolio's scope. The 12-month outlook is not validated by a 12-month backtest; only one-step origins were evaluated. Indicative ranges are not calibrated guarantees. Synthetic requirements and recommendations are not client interviews or measured commercial impact.

All data in this project is synthetic and simulated for educational and portfolio purposes.
