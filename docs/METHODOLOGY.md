# Methodology and analytical contracts

## What this product does
MERIDIAN turns a simulated B2B sales process into a traceable chain: source events → quality controls → warehouse → SQL and Python measures → bookings forecast and risk → management action. It is designed primarily for Business Analyst, BI and sales/revenue analytics roles. No machine-learning classifier is necessary.

## Data provenance and grain
All data in this project is synthetic and simulated for educational and portfolio purposes.

Default generation starts with 200,000 opportunities, 48 simulated representatives and roughly one customer for every twelve opportunities. Activities and stage visits add fact rows; 200,000 is not the total count across every table. The seed and snapshot are in config/config.yaml. Opportunity amounts depend on segment, company size, industry, product, contract term and relationship. Engagement, source, representative variation, competitor, decision makers, deal size, discount, creation season and stage duration affect probabilistic advancement. Long journeys are right-censored at snapshot. No future outcomes are saved.

A deal may lose at any stage. Every successful progression in this version moves to the next stage; backward movement, reopened opportunities and successful stage skips are outside scope. Accounts and customers are one-to-one for explainability. Stage/activity tables are trusted sources used to repair deliberately damaged opportunity extracts; this is a declared source hierarchy, not recovery of impossible information.

## Cleaning and storage
Raw Parquet preserves injected issues. Repair source hierarchy and quarantine are described in BUSINESS_RULES.md. Quality percentages use affected opportunity records, not number of cells; overlapping classes must not be summed. Customer duplicates are separately counted. Optional missing close dates on open deals and missing next actions remain legitimate. SQLite is built in a temporary sibling database, indexed and checked before replacing the published file. Referential checks are performed in Python; this is an analytical warehouse, not a transactional CRM. Processed Parquet supports inspection and Power BI export through SQLite/CSV.

## SQL and cohort discipline
The library contains 42 executable questions using CTEs, joins, windows, ranking, conditional aggregates, cohort analysis and date calculations. Funnel conversion uses actual stage-event exits. It is never inferred from the current-stage inventory. Creation cohort, current snapshot and calendar bookings are three distinct scopes. Revenue growth SQL may include a partial final quarter; never compare it with a full quarter without labelling it.

## Forecast design and evaluation
The forecast target is net booked contract value in a complete calendar month. It is not recognized revenue, recurring revenue, margin or cash. Candidate historical models are MA3, simple exponential smoothing with alpha=.3 and seasonal naive. Each is evaluated alone and blended with reconstructed weighted pipeline at 25% and 50%. At each origin, only deals created, stages entered and outcomes closed by cutoff are used. Expected dates and initial amounts are immutable fields in this simulation; using revised CRM dates without historical snapshots would leak information in a real implementation.

The first six of the final twelve historical months form validation and the later six form test. Lowest validation WAPE selects the model; tie-break uses MAE. The winning specification is evaluated on held-out months and refitted to all observed data for twelve future months. If a history-only candidate wins, pipeline remains a separate current-data cross-check, not a secretly forced blend. WAPE is the primary scale-adjusted metric; MAE/RMSE are INR, signed bias reveals direction, and MAPE excludes zero actual months. Only one-step forecasts are evaluated. Long-horizon accuracy is unproven.

Range width is the validation 80th-percentile absolute error times square root of horizon; six calibration observations are too few to claim guaranteed coverage. Aggregate bounds sum monthly bounds and are indicative. Regional backtests repeat the same procedure within each region, not an allocation of national accuracy.

For a mid-month snapshot, training ends at the previous complete month and the forecast begins with the next complete month. The partial current month is skipped in the seasonal baseline and horizon scaling as well as in the displayed calendar; partial actuals are not mixed with a full-month prediction.

## Risk, scenarios and recommendations
Risk and health are transparent policy scores; neither is a calibrated win/loss model. Stage historical conversion is separate from generator latent probabilities. The scenario engine recomputes per-deal value, probability and timing under seven inputs. Exposure describes the amount subject to a rule, not revenue that a recommendation will recover. Recommendations always contain an observed denominator, quantified exposure where meaningful, an owner and a proposed action.

## Statistics and limitations
Source win rates use Wilson intervals and a chi-square association test. Repeated customers/reps violate strict independence, so inferential outputs are educational and effect-size-first. Won-only cycles are subject to selection bias; open visits are explicitly censored. There is no causal attribution, real CRM integration, production security, actual transactions or accounting recognition schedule. A future production version needs historical CRM snapshots, governed metric definitions, clustered uncertainty, access control, scheduled ingestion and prospective business validation.
