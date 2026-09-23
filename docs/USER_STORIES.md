# User stories and acceptance criteria

## US01 — Command Center

As a CEO, I want to see year-to-date bookings against elapsed-month quota, so that I can understand progress.

Acceptance: Actuals use actual close dates and the same period as quota.

## US02 — Revenue Outlook

As a CEO, I want to see a future bookings outlook, so that I can plan capacity.

Acceptance: Twelve future months are shown with an explicit model and range.

## US03 — Pipeline Flow

As a Sales Director, I want to see active pipeline by stage, so that I can allocate coaching effort.

Acceptance: Clicking a stage lane shows records in that stage only.

## US04 — Action Queue

As a Sales Manager, I want to identify stale opportunities, so that I can prioritize contact.

Acceptance: Only active opportunities with activity gaps above 21 days are counted as stale.

## US05 — Opportunity Detail

As a Sales Representative, I want to open an opportunity timeline, so that I can understand its journey.

Acceptance: Only events whose opportunity ID matches the selected deal appear.

## US06 — Opportunity Detail

As a Sales Representative, I want to review risk reasons, so that I can know what action to take.

Acceptance: Every triggered risk rule appears with an associated action.

## US07 — Methodology

As a Revenue Operations, I want to audit data repairs, so that I can trust the source.

Acceptance: Raw and clean defect rates and quarantine counts are available.

## US08 — Data Explorer

As a Finance Analyst, I want to reconcile net contract value, so that I can avoid overstating bookings.

Acceptance: Net equals gross times one minus percentage discount within one paisa.

## US09 — Funnel Diagnostics

As a Sales Director, I want to measure stage exit conversion, so that I can locate bottlenecks.

Acceptance: Advanced plus lost plus pending equals stage entries.

## US10 — Funnel Diagnostics

As a Sales Manager, I want to inspect lost-value reasons, so that I can improve qualification.

Acceptance: Pareto cumulative share ends at 100% when lost value is nonzero.

## US11 — Customer & Market

As a Business Analyst, I want to compare commercial regions, so that I can investigate uneven performance.

Acceptance: Metrics recalculate from the selected regional cohort.

## US12 — Sales Performance

As a Sales Manager, I want to review quota and cycle alongside win rate, so that I can avoid simplistic rep rankings.

Acceptance: The table includes quota, actuals, win rate, pipeline and cycle.

## US13 — Opportunity Desk

As a Data Analyst, I want to search for a deal, so that I can find evidence efficiently.

Acceptance: Search treats user input literally, including regex metacharacters.

## US14 — Data Explorer

As a Data Analyst, I want to choose displayed columns, so that I can focus an export.

Acceptance: Downloaded CSV contains exactly the selected columns.

## US15 — Data Explorer

As a Data Analyst, I want to sort records by value or risk, so that I can prioritize investigation.

Acceptance: Ascending and descending controls change row order.

## US16 — Opportunity Desk

As a Sales Manager, I want to filter by status and creation date, so that I can inspect a cohort.

Acceptance: Date boundaries are inclusive and closed/open status is respected.

## US17 — Revenue Outlook

As a Finance Analyst, I want to download forecast evidence, so that I can reconcile planning models.

Acceptance: CSV includes every forecast period, not only displayed rows.

## US18 — Scenario Lab

As a Business Analyst, I want to change win assumptions, so that I can compare sensitivity.

Acceptance: Increasing win probability cannot lower revenue when other inputs stay fixed.

## US19 — Scenario Lab

As a Commercial Lead, I want to change discounts, so that I can understand net booking impact.

Acceptance: Increasing discount cannot increase net bookings with other inputs fixed.

## US20 — Scenario Lab

As a Sales Manager, I want to change remaining cycle duration, so that I can assess timing.

Acceptance: Deals crossing the 90-day eligibility boundary enter or leave projection.

## US21 — Scenario Lab

As a Revenue Operations, I want to add hypothetical opportunities, so that I can assess capacity assumptions.

Acceptance: New deals use documented cohort averages and an explicit cycle assumption.

## US22 — Scenario Lab

As a CEO, I want to change a planning target, so that I can see the target gap.

Acceptance: Target changes affect attainment and gap, not forecast revenue itself.

## US23 — Revenue Outlook

As a Data Analyst, I want to audit forecast selection, so that I can prevent optimistic evaluation.

Acceptance: Validation precedes test and selected-model test metrics remain separate.

## US24 — Opportunity Detail

As a Business Analyst, I want to inspect health components, so that I can defend scoring logic.

Acceptance: Eight bounded components sum to the displayed health score.

## US25 — Command Center

As a Sales Director, I want to inspect concentration, so that I can avoid reliance on a few deals.

Acceptance: Top-ten share equals ten largest open values divided by all open value.

## US26 — Customer & Market

As a Business Analyst, I want to inspect statistical uncertainty, so that I can avoid overinterpreting differences.

Acceptance: Wilson intervals and test assumptions accompany source win rates.

## US27 — SQL library

As a Data Analyst, I want to run reusable SQL, so that I can reproduce commercial answers.

Acceptance: Every statement executes against the published database.

## US28 — All workspaces

As a Sales Manager, I want to restrict commercial scope, so that I can review my responsibility.

Acceptance: Global region and team filters apply consistently to records and applicable quotas.

## US29 — Customer & Market

As a Product Analyst, I want to compare product conversion, so that I can identify investigation opportunities.

Acceptance: Product metrics display denominators and no invented product quota.

## US30 — All workspaces

As a Any user, I want to receive a helpful empty-state message, so that I can recover from restrictive filters.

Acceptance: No matching rows produce a clear message rather than a traceback.
