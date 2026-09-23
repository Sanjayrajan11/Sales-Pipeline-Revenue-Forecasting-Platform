# KPI dictionary

Currency is INR, percentages are stored as fractions except raw discount_percentage and engagement_score. Empty denominators return N/A. Every display has a scope: creation cohort, active snapshot or close-date calendar period.

## Pipeline Value

**What:** Total opportunity value in the selected creation cohort, including resolved deals.

**Why / business interpretation:** Understand the size of the cohort; it is not current open pipeline.

**Formula:** `sum(net_deal_value)`.

## Closed-Won Revenue

**What:** Net booked contract value on won deals.

**Why / business interpretation:** Measure commercial outcomes; calendar reports filter actual close dates.

**Formula:** `sum(net_deal_value where Closed Won)`.

## Closed-Lost Value

**What:** Potential booked value on lost deals.

**Why / business interpretation:** Prioritize loss reviews; this is not recognized revenue leakage.

**Formula:** `sum(net_deal_value where Closed Lost)`.

## Open Pipeline

**What:** Active face-value opportunity inventory.

**Why / business interpretation:** Understand current inventory without assuming conversion.

**Formula:** `sum(net_deal_value where Open or Stalled)`.

## Weighted Pipeline

**What:** Stage-conditioned expected active value.

**Why / business interpretation:** Discount inventory for historical conversion; not a calibrated guaranteed forecast.

**Formula:** `sum(active net_deal_value × win_probability)`.

## Win Rate

**What:** Success among resolved opportunities.

**Why / business interpretation:** Compare conversion with counts and deal mix; pending deals are excluded.

**Formula:** `won_count / (won_count + lost_count)`.

## Stage Conversion Rate

**What:** Advancement among observed exits.

**Why / business interpretation:** Identify process attrition while displaying pending visits separately.

**Formula:** `advanced_exits / all_observed_exits`.

## Average Deal Size

**What:** Mean net won deal value.

**Why / business interpretation:** Understand realized booking economics; sensitive to large contracts.

**Formula:** `won_net_value / won_count`.

## Median Deal Size

**What:** Middle won net value.

**Why / business interpretation:** Understand typical wins without large-deal distortion.

**Formula:** `median(won net_deal_value)`.

## Average Sales Cycle

**What:** Mean completed won journey duration.

**Why / business interpretation:** Assess speed; not an estimate of completion time for pending deals.

**Formula:** `mean(actual_close_date − created_date on won)`.

## Pipeline Coverage

**What:** Period pipeline relative to remaining quota.

**Why / business interpretation:** Coverage is undefined when the remaining target is zero; due-date scope matters.

**Formula:** `period_open_value / max(0, period_target − period_actual)`.

## Quota Attainment

**What:** Bookings against matched quota.

**Why / business interpretation:** Compare the same representative/region and time period; product quota is unallocated.

**Formula:** `period_actual / period_target`.

## Revenue Growth

**What:** Change between booking periods.

**Why / business interpretation:** Investigate trend; partial calendar periods must be identified.

**Formula:** `current_bookings / prior_bookings − 1`.

## Forecast Accuracy

**What:** Aggregate absolute forecast error relative to actual.

**Why / business interpretation:** Lower is better. Do not describe WAPE as an accuracy percentage without context.

**Formula:** `WAPE = sum(abs(forecast−actual))/sum(abs(actual))`.

## Forecast Variance

**What:** Signed forecast-versus-actual error.

**Why / business interpretation:** Positive means overforecast. Future variance is unavailable until actuals exist.

**Formula:** `forecast − actual`.

## Deal Velocity

**What:** Indicative daily booking throughput.

**Why / business interpretation:** A heuristic mixing stock and history, useful for sensitivity rather than a forecast guarantee.

**Formula:** `open_count × resolved_win_rate × average_won_size / average_won_cycle`.

## Opportunity Aging

**What:** Elapsed age of active deals.

**Why / business interpretation:** Prioritize aging inventory; closed ages stop at actual close.

**Formula:** `mean(snapshot − created_date on active)`.

## Stale Opportunity Rate

**What:** Share of active deals without recent activity.

**Why / business interpretation:** Measure follow-up exposure, not probability of loss.

**Formula:** `active_count(activity_gap_days > 21) / active_count`.

## Pipeline Concentration

**What:** Dependence on a few large active deals.

**Why / business interpretation:** High concentration merits executive sponsorship; no universal cutoff is assumed.

**Formula:** `sum(top N active net values) / sum(active net values), N=5,10,20`.

## Average Discount

**What:** Unweighted average recorded percentage.

**Why / business interpretation:** Compare pricing behavior while recognizing it is not value-weighted.

**Formula:** `mean(discount_percentage)`.

## Revenue per Sales Rep

**What:** Cohort bookings per represented owner.

**Why / business interpretation:** Productivity proxy; full organization capacity is not the denominator.

**Formula:** `won_value / distinct cohort sales_rep_id`.

## Revenue per Customer

**What:** Cohort bookings per represented customer.

**Why / business interpretation:** Commercial yield includes customers that did not win.

**Formula:** `won_value / distinct cohort customer_id`.

## Lead-to-Win Rate

**What:** Observed wins in creation cohort.

**Why / business interpretation:** Recent cohorts are immature; show pending counts.

**Formula:** `won_count / all_opportunities`.

## Proposal-to-Win Rate

**What:** Observed wins among deals that reached Proposal.

**Why / business interpretation:** A historical reach cohort measure, not current proposal inventory conversion.

**Formula:** `won_reached_Proposal / reached_Proposal`.

## Negotiation-to-Win Rate

**What:** Observed wins among deals that reached Negotiation.

**Why / business interpretation:** Pending deals reduce observed yield; resolved-exit conversion is a separate measure.

**Formula:** `won_reached_Negotiation / reached_Negotiation`.

## Weighted Coverage

**What:** Expected period pipeline versus remaining quota.

**Why / business interpretation:** More conservative than raw coverage; undefined with no remaining target.

**Formula:** `period_weighted_pipeline / remaining_target`.

## Revenue Gap

**What:** Planning shortfall.

**Why / business interpretation:** Negative means projected excess; not a proven lost/recovered amount.

**Formula:** `target − expected_bookings`.

## Forecast Bias

**What:** Average signed forecast error.

**Why / business interpretation:** Detect systematic optimism or conservatism.

**Formula:** `mean(forecast − actual)`.

## Stalled Rate

**What:** Explicit stalled status among active deals.

**Why / business interpretation:** The simulation marks active deals stalled when activity gap exceeds 30 days.

**Formula:** `stalled_count / active_count`.
