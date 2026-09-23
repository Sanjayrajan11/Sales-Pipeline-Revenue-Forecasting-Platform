# Data dictionary

All data is synthetic. Currency is INR. Empty closed dates are valid for active deals. SQLite stores booleans as 0/1 and dates as ISO text; Parquet preserves logical types.

## customers — 16,666 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| customer_id | int64 | Customer master foreign key |
| customer_name | str | Explicitly synthetic enterprise display name |
| city | str | City from geography master |
| state | str | State from geography master, consistent with city/region |
| region | str | North / South / East / West India |
| industry | str | Simulated account commercial industry |
| customer_segment | str | SMB / Mid-market / Enterprise |
| company_size | int64 | Simulated employee count; input to deal value |
| annual_revenue_band | str | Simulated company annual-revenue size band, not project bookings |
| existing_customer | bool | Boolean previous-customer relationship; not based on future outcomes |
| customer_since | datetime64[us] | Date synthetic account was known to the business |
| customer_health_score | int64 | Generated 35–95 customer relationship attribute, separate from deal health |
| account_manager | int64 | Authoritative account-owner representative key |
| customer_lifetime_value | float64 | Sum of observed won net contracts in modeled history; not predictive CLV |
| active_products | int64 | Distinct products ever won in modeled history; not verified active subscriptions |

## accounts — 16,666 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| account_id | int64 | Account key; one account per customer in this model |
| account_manager | int64 | Authoritative account-owner representative key |
| customer_id | int64 | Customer master foreign key |

## sales_reps — 48 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| sales_rep_id | int64 | Representative key / opportunity owner |
| sales_rep_name | str | Simulated representative display label |
| region | str | North / South / East / West India |
| team | str | Regional commercial team name |
| sales_team_id | int64 | Regional commercial team key |
| experience_years | int64 | Representative experience in whole years |
| manager | str | Simulated regional manager label |
| territory | str | Assigned sales region |
| hire_date | datetime64[us] | Simulated rep employment start |
| monthly_target | float64 | Planning quota per rep-month in INR; scaled with dataset size |
| annual_target | float64 | Twelve times representative monthly quota, INR |

## sales_teams — 4 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| sales_team_id | int64 | Regional commercial team key |
| team | str | Regional commercial team name |
| region | str | North / South / East / West India |
| manager | str | Simulated regional manager label |

## products — 4 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| product_id | int64 | Product catalogue key |
| product | str | Technology/service product label |
| product_category | str | Software or Services |
| base_price | int64 | Catalogue base price, INR |

## regions — 8 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| city | str | City from geography master |
| state | str | State from geography master, consistent with city/region |
| region | str | North / South / East / West India |

## industries — 5 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| industry | str | Simulated account commercial industry |

## lead_sources — 5 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| lead_source | str | Referral / Partner / Inbound / Outbound / Event |

## stages — 6 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| sales_stage | str | Current stage on opportunity, visited stage on history |
| stage_order | int64 | Zero-based forward process order |

## opportunities — 198,000 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| opportunity_id | int64 | Unique sales opportunity key; opportunity table grain |
| customer_id | int64 | Customer master foreign key |
| city | str | City from geography master |
| state | str | State from geography master, consistent with city/region |
| region | str | North / South / East / West India |
| industry | str | Simulated account commercial industry |
| customer_segment | str | SMB / Mid-market / Enterprise |
| company_size | int64 | Simulated employee count; input to deal value |
| existing_customer | bool | Boolean previous-customer relationship; not based on future outcomes |
| customer_health_score | int64 | Generated 35–95 customer relationship attribute, separate from deal health |
| account_id | int64 | Account key; one account per customer in this model |
| sales_rep_id | int64 | Representative key / opportunity owner |
| sales_team_id | int64 | Regional commercial team key |
| created_date | datetime64[us] | Opportunity creation / first Lead entry date |
| product_id | int64 | Product catalogue key |
| product | str | Technology/service product label |
| product_category | str | Software or Services |
| lead_source | str | Referral / Partner / Inbound / Outbound / Event |
| contract_type | str | Annual / Multi-year / Project; value is total booked contract value |
| deal_type | str | New business / Renewal / Expansion |
| new_or_existing_customer | str | Relationship at opportunity creation; immutable simulated attribute |
| opportunity_amount | float64 | Gross contract face value, INR |
| discount_percentage | float64 | Discount in percentage points, e.g. 10 means 10% |
| net_deal_value | float64 | Gross × (1 − discount/100), rounded to INR paisa |
| competitor_present | bool | Boolean known competitor indicator |
| competitor_name | str | Synthetic A/B/C competitor or None |
| decision_makers_count | int64 | Number of participants in buying decision |
| engagement_score | float64 | Generated 0–100 engagement index; drives probabilistic behavior |
| expected_close_date | datetime64[us] | Immutable initial expected contract close date; may be overdue |
| sales_stage | str | Current stage on opportunity, visited stage on history |
| previous_stage | str | Immediately preceding observed stage, or None at Lead |
| stage_entry_date | datetime64[us] | Start of current stage; terminal date on closed deals |
| actual_close_date | datetime64[us] | Observed terminal event date; null for Open/Stalled |
| deal_status | str | Closed Won / Closed Lost / Open / Stalled |
| lost_reason | str | Terminal loss reason, empty string for non-lost deals |
| last_activity_date | datetime64[us] | Latest observed activity event date for the deal |
| activity_gap_days | int64 | Days from latest activity to snapshot or observed close |
| next_follow_up_date | datetime64[us] | Scheduled next action; may be null or overdue |
| sales_cycle_days | float64 | Observed actual close minus creation in days; null on active deals |
| total_opportunity_age_days | int64 | Days from creation until snapshot or observed close |
| days_in_current_stage | int64 | Snapshot-minus-entry for active deals; zero for terminal current stage |
| quarter | int32 | Calendar creation quarter, 1–4 |
| month | int32 | Calendar creation month, 1–12 |
| year | int32 | Calendar creation year |
| meeting_count | int64 | Observed Meeting activity count |
| email_count | int64 | Observed Email activity count |
| call_count | int64 | Observed Phone Call activity count |
| demo_count | int64 | Observed Product Demo activity count |
| follow_up_count | int64 | Observed Follow-up activity count |
| proposal_sent | bool | Boolean stage-history evidence of reaching Proposal |
| win_probability | float64 | Resolved-stage historical Beta(1,1) estimate; 1/0 on won/lost |
| weighted_value | float64 | Active net contract value × historical stage probability; zero if closed |
| forecast_category | str | Mutually exclusive Commit / Best Case / Pipeline / Closed Won / Excluded |
| risk_score | int64 | Sum of triggered policy points, 0–100; not a loss probability |
| risk_level | str | Low / Medium / High / Critical; Closed is excluded from actioning |
| risk_drivers | str | Semicolon-separated triggered risk-rule names |
| recommended_action | str | Rule-linked operational actions; no CRM write-back is performed |
| health_stage_progression | float64 | Stage progression health contribution, 0–12.5 points; see BUSINESS_RULES.md |
| health_recency | float64 | Recency health contribution, 0–12.5 points; see BUSINESS_RULES.md |
| health_age | float64 | Age health contribution, 0–12.5 points; see BUSINESS_RULES.md |
| health_engagement | float64 | Engagement health contribution, 0–12.5 points; see BUSINESS_RULES.md |
| health_close_plan | float64 | Close plan health contribution, 0–12.5 points; see BUSINESS_RULES.md |
| health_historical_conversion | float64 | Historical conversion health contribution, 0–12.5 points; see BUSINESS_RULES.md |
| health_size_balance | float64 | Size balance health contribution, 0–12.5 points; see BUSINESS_RULES.md |
| health_next_action | float64 | Next action health contribution, 0–12.5 points; see BUSINESS_RULES.md |
| health_score | float64 | Sum of eight equally weighted bounded components; null for closed deals |
| health_category | str | Healthy / Watch / At risk / Closed |
| forecast_risk_value | float64 | Weighted pipeline × risk score/100; prioritization exposure, not calibrated expected loss |

## activities — 827,893 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| activity_id | int64 | Unique activity event key |
| opportunity_id | int64 | Unique sales opportunity key; opportunity table grain |
| activity_date | datetime64[us] | Observed interaction date within deal lifetime |
| activity_type | str | Email / Phone Call / Meeting / Product Demo / Proposal / Negotiation / Follow-up / Contract Review |
| duration_minutes | int64 | Simulated interaction duration in minutes |
| outcome | str | Engaged or No response |
| sales_rep_id | int64 | Representative key / opportunity owner |
| customer_id | int64 | Customer master foreign key |

## stage_history — 705,379 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| transition_id | int64 | Unique stage visit key |
| opportunity_id | int64 | Unique sales opportunity key; opportunity table grain |
| sales_stage | str | Current stage on opportunity, visited stage on history |
| stage_order | int64 | Zero-based forward process order |
| entry_date | datetime64[us] | Observed stage entry date |
| exit_date | datetime64[us] | Observed exit or null if right-censored |
| exit_to | str | Next stage or terminal outcome; empty while pending |
| duration_days | int64 | Completed visit duration or censored elapsed duration |

## contracts — 45,187 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| contract_id | int64 | Won contract key, one per won opportunity |
| opportunity_id | int64 | Unique sales opportunity key; opportunity table grain |
| customer_id | int64 | Customer master foreign key |
| contract_type | str | Annual / Multi-year / Project; value is total booked contract value |
| net_deal_value | float64 | Gross × (1 − discount/100), rounded to INR paisa |
| actual_close_date | datetime64[ns] | Observed terminal event date; null for Open/Stalled |

## targets — 2,688 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| period | datetime64[us] | Calendar month start / forecast period |
| sales_rep_id | int64 | Representative key / opportunity owner |
| target | float64 | Representative or aggregate monthly quota, INR |
| region | str | North / South / East / West India |

## forecast_periods — 56 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| period | datetime64[us] | Calendar month start / forecast period |

## lost_reasons — 12 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| lost_reason | str | Terminal loss reason, empty string for non-lost deals |

## competitors — 4 rows

| Field | Pandas type | Definition / unit |
| --- | --- | --- |
| competitor_name | str | Synthetic A/B/C competitor or None |

## Analytical outputs

Derived KPI, funnel, forecast, backtest, scenario, quality and recommendation tables are defined by KPI_DICTIONARY.md, METHODOLOGY.md and BUSINESS_RULES.md. Forecast errors are INR except WAPE/MAPE/bias_pct fractions. Scenario probabilities and adjustments use the units shown in the application. Each backtest row is one model × forecast origin; filter to the selected model before totaling.
