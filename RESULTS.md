# Executed project results

Calculated from the generated dataset. All data is synthetic; no real-company or recovery result is claimed.

## Dataset and quality

Snapshot: 2026-08-31; seed: 42. Generated 200,000 distinct opportunities before defect injection. Raw extract: 201,200 rows. Clean: 198,000; invalid financial records quarantined: 2,000. Customer duplicates removed: 167.

| Entity | Rows |
| --- | --- |
| customers | 16,666 |
| accounts | 16,666 |
| sales_reps | 48 |
| sales_teams | 4 |
| products | 4 |
| regions | 8 |
| industries | 5 |
| lead_sources | 5 |
| stages | 6 |
| opportunities | 198,000 |
| activities | 827,893 |
| stage_history | 705,379 |
| contracts | 45,187 |
| targets | 2,688 |
| forecast_periods | 56 |
| lost_reasons | 12 |
| competitors | 4 |

| check | affected_records | percentage |
| --- | --- | --- |
| missing_key_fields | 2012 | 1.000% |
| duplicate_opportunity | 1200 | 0.596% |
| invalid_record | 3015 | 1.499% |
| amount_outlier | 1002 | 0.498% |
| date_inconsistency | 2971 | 1.477% |
| missing_industry | 1005 | 0.500% |
| missing_rep | 1007 | 0.500% |

Clean records pass every implemented quality check. Classes overlap and must not be added. See DATA_QUALITY_REPORT.md for repair provenance.

## KPI results

| Metric | Value (INR) |
| --- | --- |
| pipeline_value | ₹1,64,68,04,43,653 |
| closed_won_revenue | ₹35,12,52,88,578 |
| closed_lost_value | ₹1,19,93,12,07,764 |
| open_pipeline | ₹9,62,39,47,311 |
| weighted_pipeline | ₹4,25,10,54,787 |
| average_deal_size | ₹7,77,332 |
| median_deal_size | ₹4,50,891 |
| ytd_target | ₹9,53,85,91,744 |
| ytd_actual | ₹8,44,29,24,461 |
| ytd_remaining_target | ₹1,09,56,67,283 |

Resolved-deal win rate: **24.26%**. Won cycle mean: 113.0 days; median: 109.0 days. Active stale share: 17.22%. Top 5 / 10 / 20 face-value pipeline shares: 0.58% / 1.06% / 1.92%. YTD attainment: 88.51%.

## Pipeline diagnostics

| stage | entered | exited | pending | conversion | drop_off | average_days_completed |
| --- | --- | --- | --- | --- | --- | --- |
| Lead | 198000 | 195813 | 2187 | 0.7618 | 0.2382 | 12.6737 |
| Qualified | 149179 | 147018 | 2161 | 0.8079 | 0.1921 | 17.6992 |
| Discovery | 118776 | 116423 | 2353 | 0.8264 | 0.1736 | 22.7255 |
| Demo | 96216 | 94782 | 1434 | 0.8573 | 0.1427 | 16.1396 |
| Proposal | 81260 | 79011 | 2249 | 0.784 | 0.216 | 27.3183 |
| Negotiation | 61948 | 60621 | 1327 | 0.7454 | 0.2546 | 20.8465 |

## Forecast and evaluation

Selected by validation WAPE: **Seasonal naive + 0% pipeline**. Held-out WAPE: **14.12%**; MAE ₹16,23,71,924; RMSE ₹16,67,66,836; signed bias -₹16,23,71,924. The pipeline candidates were evaluated but did not beat the selected history-only baseline on validation. Current weighted pipeline remains a separate cross-check.

| period | forecast | lower | upper | pipeline_contribution | target | gap_to_target |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-09 | ₹1,01,38,91,702 | ₹91,08,50,707 | ₹1,11,69,32,697 | ₹1,59,34,76,217 | ₹1,19,23,23,968 | ₹17,84,32,266 |
| 2026-10 | ₹86,10,62,856 | ₹71,53,40,884 | ₹1,00,67,84,828 | ₹99,95,44,243 | ₹1,19,23,23,968 | ₹33,12,61,112 |
| 2026-11 | ₹88,92,52,734 | ₹71,07,80,496 | ₹1,06,77,24,972 | ₹87,40,54,596 | ₹1,19,23,23,968 | ₹30,30,71,234 |
| 2026-12 | ₹76,91,53,099 | ₹56,30,71,110 | ₹97,52,35,088 | ₹51,17,00,567 | ₹1,19,23,23,968 | ₹42,31,70,869 |
| 2027-01 | ₹76,88,44,609 | ₹53,84,37,941 | ₹99,92,51,277 | ₹19,27,33,710 | ₹1,19,23,23,968 | ₹42,34,79,359 |
| 2027-02 | ₹77,21,79,065 | ₹51,97,81,206 | ₹1,02,45,76,925 | ₹6,10,56,595 | ₹1,19,23,23,968 | ₹42,01,44,903 |
| 2027-03 | ₹99,33,32,304 | ₹72,07,11,457 | ₹1,26,59,53,150 | ₹1,47,68,531 | ₹1,19,23,23,968 | ₹19,89,91,664 |
| 2027-04 | ₹96,36,16,913 | ₹67,21,72,969 | ₹1,25,50,60,857 | ₹37,20,328 | ₹1,19,23,23,968 | ₹22,87,07,055 |
| 2027-05 | ₹1,21,22,83,894 | ₹90,31,60,910 | ₹1,52,14,06,877 | ₹0 | ₹1,19,23,23,968 | -₹1,99,59,926 |
| 2027-06 | ₹1,21,96,53,809 | ₹89,38,09,574 | ₹1,54,54,98,044 | ₹0 | ₹1,19,23,23,968 | -₹2,73,29,841 |
| 2027-07 | ₹1,27,25,41,567 | ₹93,07,93,250 | ₹1,61,42,89,884 | ₹0 | ₹1,19,23,23,968 | -₹8,02,17,599 |
| 2027-08 | ₹1,24,04,72,300 | ₹88,35,27,824 | ₹1,59,74,16,776 | ₹0 | ₹1,19,23,23,968 | -₹4,81,48,332 |

Next three months: forecast **₹2,76,42,07,292**, target **₹3,57,69,71,904**, gap **₹81,27,64,612**. Twelve-month forecast: ₹11,97,62,84,852. Range is indicative and long-horizon accuracy is not established by one-month backtests.

## Deal risk

| risk_level | deals | face_value | weighted_value |
| --- | --- | --- | --- |
| Critical | 182 | ₹20,92,83,215 | ₹12,95,52,994 |
| High | 762 | ₹78,10,87,777 | ₹46,35,46,803 |
| Low | 8332 | ₹6,34,17,06,709 | ₹2,51,68,56,788 |
| Medium | 2435 | ₹2,29,18,69,611 | ₹1,14,10,98,203 |

Policy classifications are not loss probabilities. Closed opportunities are excluded.

## Scenario output

| scenario | projected_revenue | projected_won_deals | expected_pipeline | target | target_attainment | revenue_gap | pipeline_required | eligible_existing_deals | eligible_additional_deals |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline | ₹3,43,97,49,812 | 4531.66318778781 | ₹7,05,25,23,158 | ₹3,57,69,71,904 | 96.16% | ₹13,72,22,092 | ₹28,13,46,619 | 9556 | 0 |
| +5pp win, 10% faster cycle | ₹4,05,11,56,340 | 5274.930315764061 | ₹7,72,01,29,613 | ₹3,57,69,71,904 | 113.26% | -₹47,41,84,436 | ₹0 | 10272 | 0 |

The example changes win probability by +5 percentage points and remaining cycle by −10%. This is a conditional projection, not an observed improvement.

## Recommendations and evidence

- **Stale opportunities:** 2,017 of 11,711 open/stalled deals. Impact: ₹1,73,55,64,584 potential bookings exposed; not recoverable revenue. Action: Contact the customer within two business days.
- **High-value risky deals:** 167 of 11,711 open/stalled deals. Impact: ₹55,68,12,536 potential bookings exposed; not recoverable revenue. Action: Arrange manager and commercial review.
- **Expected close approaching or overdue:** 2,344 of 11,711 open/stalled deals. Impact: ₹1,59,02,27,848 potential bookings exposed; not recoverable revenue. Action: Validate procurement milestones and update the close plan.
- **No scheduled future action:** 5,352 of 11,711 open/stalled deals. Impact: ₹4,47,30,17,712 potential bookings exposed; not recoverable revenue. Action: Schedule a specific follow-up date.
- **Low engagement:** 2,608 of 11,711 open/stalled deals. Impact: ₹2,12,56,53,534 potential bookings exposed; not recoverable revenue. Action: Identify an active customer sponsor.
- **Lower observed conversion: Outbound:** 17.7% resolved-deal win rate; 49,655 total opportunities. Impact: ₹2,12,05,18,839 current pipeline in this cohort. Action: Review lead_source qualification and deal mix before changing investment.
- **Lower observed conversion: South:** 23.8% resolved-deal win rate; 49,976 total opportunities. Impact: ₹2,31,28,67,304 current pipeline in this cohort. Action: Review region qualification and deal mix before changing investment.
- **Lower observed conversion: Data Advisory:** 24.1% resolved-deal win rate; 49,573 total opportunities. Impact: ₹3,18,80,29,235 current pipeline in this cohort. Action: Review product qualification and deal mix before changing investment.
- **Stage bottleneck: Negotiation:** 25.5% lost among 60,621 observed exits; 1,327 visits still pending. Impact: Qualification or commercial process may constrain conversion; no causal effect estimated. Action: Review a sample of lost deals and validate stage exit criteria.
- **Largest lost-value reason: Competitor selected:** 36,831 lost deals; 26.2% of lost value. Impact: ₹31,44,85,22,647 historical potential bookings lost. Action: Audit reason coding and run a targeted loss review.
- **Largest forecast contributors:** Top ten deals contribute 1.46% of weighted active pipeline. Impact: ₹6,20,21,382 weighted bookings depend on these close plans. Action: Review the top-ten deal plans and executive sponsorship weekly.
- **Region below elapsed-month target: East:** ₹2,10,60,86,349 booked versus ₹2,38,84,50,864 YTD target; 88.2% attainment. Impact: ₹28,23,64,515 booking shortfall. Action: Reconcile close timing, capacity and qualification with the regional manager.
- **Region below elapsed-month target: North:** ₹2,19,93,47,066 booked versus ₹2,27,91,62,536 YTD target; 96.5% attainment. Impact: ₹7,98,15,470 booking shortfall. Action: Reconcile close timing, capacity and qualification with the regional manager.
- **Region below elapsed-month target: South:** ₹2,02,42,45,344 booked versus ₹2,45,75,72,792 YTD target; 82.4% attainment. Impact: ₹43,33,27,448 booking shortfall. Action: Reconcile close timing, capacity and qualification with the regional manager.
- **Region below elapsed-month target: West:** ₹2,11,32,45,702 booked versus ₹2,41,34,05,552 YTD target; 87.6% attainment. Impact: ₹30,01,59,850 booking shortfall. Action: Reconcile close timing, capacity and qualification with the regional manager.

## Use and verification

Run `python run_pipeline.py`, `python -m pytest -q`, then `streamlit run app.py`. Open http://localhost:8501 in Chrome. The README covers setup and repository structure. docs/VALIDATION.md records the final executed tests/browser evidence. docs/INTERVIEW_GUIDE.md contains 66 explained questions; docs/TWO_MINUTE_EXPLANATION.md and docs/RESUME_BULLETS.md support portfolio presentation. Power BI is a guide/DAX deliverable, not an executed .pbix.
