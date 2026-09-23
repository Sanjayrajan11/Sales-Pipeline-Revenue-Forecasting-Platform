# Business requirements — MERIDIAN

## Background and problem
The simulated India-based B2B technology/services company lacks a shared view of opportunity progression, expected bookings and follow-up ownership. Spreadsheet totals mix closed deals with current pipeline and conceal stage bottlenecks. Leadership needs defensible decisions rather than additional charts.

## Objectives and decisions
1. Establish a reconciled, repeatable source for pipeline and net booked contract value.
2. Identify stale deals and commercial bottlenecks with traceable evidence.
3. Compare a bookings forecast with quota, including uncertainty and held-out error.
4. Prioritize manager interventions and explore assumptions without claiming causal gains.
5. Give a fresher a system whose formulas, assumptions and implementation can be defended.

## Stakeholders and needs
| Stakeholder | Need | Decision / acceptance evidence |
|---|---|---|
| CEO / Leadership | Booking outlook and target gap | See period-aligned actuals, forecast and quota |
| Sales Director | Stage losses and concentrated exposure | Inspect transitions, pending visits and top-deal share |
| Sales Managers | Fair multi-dimensional performance comparisons | Review period bookings, cycle, win rate and quota together |
| Sales Representatives | Concrete next steps | Open a deal and read activity history and risk drivers |
| Finance Team | Reconciled booked value and forecast | Reconcile net amount; avoid confusing bookings with recognized revenue |
| Revenue Operations | Consistent stages, data quality and ownership | Review cleaning audit and malformed-record quarantine |
| Business Analysts | Traceable requirements and process changes | Follow stories to implementation and acceptance checks |
| Data Analysts | SQL, records and reusable measures | Execute every query and export filtered records |

## Functional requirements
FR01 Generate deterministic configurable sales data and relational events.
FR02 Detect, repair or quarantine defects with documented denominators.
FR03 Publish queryable SQLite tables after referential and financial validation.
FR04 Calculate cohort, period, funnel, cycle, loss and concentration measures.
FR05 Reconstruct historical snapshots and backtest explainable forecasts.
FR06 Explain active-deal risk and every health-score component.
FR07 Provide global commercial filters and local record/date/source filters.
FR08 Support searchable, sortable records, per-deal drill-down and CSV export.
FR09 Recalculate all seven scenario assumptions and show baseline differences.
FR10 Generate evidence-linked recommendations with owners and priorities.
FR11 Provide Power BI modeling/DAX instructions and reproducible SQL.
FR12 Launch locally in Chrome and recover gracefully from empty/invalid data.

## Non-functional requirements
NFR01 Reproducibility: fixed seed, fixed snapshot, pinned dependencies and run manifest.
NFR02 Integrity: no post-outcome inputs in historical forecast snapshots.
NFR03 Usability: black background with white text and grayscale charts, horizontal navigation/filter scope, keyboard-labelled controls, no color-only risk signals.
NFR04 Performance: indexed detail queries and cached aggregate/forecast reads; bounded displayed tables with full exports.
NFR05 Portability: repository-relative paths; Python 3.12; no paid service or API key.
NFR06 Reliability: numerical tests, SQL execution gate, page tests and browser evidence.
NFR07 Privacy: all records are explicitly synthetic; local host binds to loopback.

## Business rules and KPI scope
Revenue means net booked contract value at actual close, not cash collection or accounting recognition. Net = gross × (1 − discount/100). Win rate = won / (won + lost). Open includes stalled. Stage conversion = advanced / observed exits. Pending stage visits do not imply loss. Coverage uses remaining period target; a zero denominator displays N/A. Product/segment quotas are not allocated and therefore no quota is invented for them. See KPI_DICTIONARY.md and BUSINESS_RULES.md.

## Assumptions
Requirements are analyst-authored for a simulated company, not elicited from real stakeholders. One customer has one account. Initial expected close dates and amounts are immutable in this simulation. Contract value is booked in full when won, including multi-year contracts. Monthly quotas are planning assumptions scaled with dataset size, not inferred business outcomes.

## Constraints and risks
Single-user local analytics; no CRM write-back, authentication or accounting ledger. Censored recent cohorts distort naive conversion comparisons. Synthetic associations are designed, not evidence about real Indian industries. Large data can increase memory usage. Forecast behavior may deteriorate with real-world regime changes. Data repair depends on trusted master/event tables.

## Acceptance criteria and traceability
Given the default config, one pipeline command generates data, produces reports, executes all 42 SQL queries and publishes a valid database. Given an empty filter, the UI explains the empty state. Given a deal ID, stage and activity records match that key. Given a scenario input change, outputs follow documented equations. Given a held-out origin, no later outcome enters forecast training. Tests, docs/USER_STORIES.md and docs/VALIDATION.md provide execution evidence; file creation alone is insufficient.
