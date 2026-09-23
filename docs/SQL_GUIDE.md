# SQL business question index

SQLite dialect. Run `python scripts/validate_sql.py` after the pipeline. Percentages are fractions; currency is INR. No user-provided SQL is accepted by the app.

## funnel_queries.sql

- Q07 Stage conversion: resolved exits, not counts of current-stage inventory.
- Q08 Largest observed stage loss fraction, plus pending visits.
- Q29 Completed stage duration and sample size.
- Q30 Still-open visits: ages are right-censored, not completed duration estimates.
- Q31 Product conversion with observed closed counts.
- Q42 Creation cohort outcomes, preserving pending counts to expose maturity bias.

## pipeline_queries.sql

- Q01 Total lifetime cohort opportunity value, including resolved opportunities.
- Q04 Current open and stalled pipeline.
- Q05 Probability-weighted pipeline, not all-open face value.
- Q09 Stale deals needing contact, policy threshold >21 days.
- Q19 Opportunities exceeding the observed mean won cycle.
- Q22 Month-over-month newly created pipeline, not historical open snapshots.
- Q23 Top 5/10/20 pipeline concentration using deterministic row numbers.
- Q24 Upcoming-month raw coverage. Overdue deals roll into the month as in forecast policy.
- Q25 Close-date pressure with stale activity: explainable slip watch, not probability.
- Q28 Repeat-customer opportunities and realized bookings.
- Q35 Largest policy-weighted forecast exposures; not an expected-loss estimate.
- Q37 Stalled share of active pipeline count and value.
- Q38 No recent activity, joined to owner for follow-up.
- Q40 Management attention queue ordered by exposure, preserving individual reasons.

## revenue_queries.sql

- Q02 Closed-won booked contract value; not accounting-recognized revenue.
- Q03 Potential contract value lost.
- Q12 Revenue and tied rank across industries.
- Q15 Product booking mix.
- Q16 Average won deal size.
- Q17 Exact median in SQLite via two central row numbers.
- Q18 Won cycle percentiles: nearest-rank P25/P75/P90, explicitly not interpolation.
- Q20 Lost-value Pareto: cumulative contribution by reason.
- Q21 Calendar quarter booking growth. Final quarter may be partial, label in consumers.
- Q27 Segments with valuable wins and long cycles; no causal interpretation.
- Q32 Industry average deal size and deterministic dense rank.
- Q33 Source contribution to total won bookings.
- Q34 Regional held-out one-month forecast error; selected regional models.
- Q41 Rolling three complete monthly booking observations and next-month actual.

## sales_performance_queries.sql

- Q06 Resolved-deal win rate with an explicit closed-deal denominator.
- Q10 Rep outcome mix; do not interpret volume-free win rate as a personnel score.
- Q11 Open and weighted pipeline by sales representative.
- Q13 Regional year-to-snapshot target attainment, with matched monthly quotas.
- Q14 Lead-source quality: resolved win rate and average size alongside volume.
- Q26 Reps with above-average open value and below-company resolved conversion.
- Q36 Quarterly target attainment, preserving full-quarter target for partial quarters.
- Q39 Top-three deal concentration per rep with windowed partitions.
