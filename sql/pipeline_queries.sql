-- Q01 Total lifetime cohort opportunity value, including resolved opportunities.
SELECT SUM(net_deal_value) AS pipeline_value FROM opportunities;
-- Q04 Current open and stalled pipeline.
SELECT COUNT(*) AS deals, SUM(net_deal_value) AS open_pipeline FROM open_pipeline;
-- Q05 Probability-weighted pipeline, not all-open face value.
SELECT SUM(weighted_value) AS weighted_pipeline FROM open_pipeline;
-- Q09 Stale deals needing contact, policy threshold >21 days.
SELECT opportunity_id, net_deal_value, activity_gap_days FROM open_pipeline WHERE activity_gap_days > 21 ORDER BY net_deal_value DESC;
-- Q19 Opportunities exceeding the observed mean won cycle.
SELECT opportunity_id, total_opportunity_age_days FROM open_pipeline WHERE total_opportunity_age_days > (SELECT AVG(sales_cycle_days) FROM won_bookings);
-- Q22 Month-over-month newly created pipeline, not historical open snapshots.
WITH m AS (SELECT STRFTIME('%Y-%m',created_date) month, SUM(net_deal_value) value FROM opportunities GROUP BY 1)
SELECT month,value,LAG(value) OVER(ORDER BY month) previous_value, value/NULLIF(LAG(value) OVER(ORDER BY month),0)-1 AS growth FROM m;
-- Q23 Top 5/10/20 pipeline concentration using deterministic row numbers.
WITH ranked AS (SELECT *,ROW_NUMBER() OVER(ORDER BY net_deal_value DESC,opportunity_id) rn FROM open_pipeline)
SELECT SUM(CASE WHEN rn<=5 THEN net_deal_value ELSE 0 END)/NULLIF(SUM(net_deal_value),0) top5_share,
SUM(CASE WHEN rn<=10 THEN net_deal_value ELSE 0 END)/NULLIF(SUM(net_deal_value),0) top10_share,
SUM(CASE WHEN rn<=20 THEN net_deal_value ELSE 0 END)/NULLIF(SUM(net_deal_value),0) top20_share FROM ranked;
-- Q24 Upcoming-month raw coverage. Overdue deals roll into the month as in forecast policy.
WITH period AS (SELECT MIN(period) p FROM forecast), quota AS (SELECT SUM(target) value FROM targets WHERE period=(SELECT p FROM period))
SELECT SUM(net_deal_value)/NULLIF((SELECT value FROM quota),0) coverage FROM open_pipeline WHERE expected_close_date < DATETIME((SELECT p FROM period),'+1 month');
-- Q25 Close-date pressure with stale activity: explainable slip watch, not probability.
SELECT opportunity_id, expected_close_date, activity_gap_days, risk_drivers FROM open_pipeline WHERE activity_gap_days>21 AND expected_close_date < (SELECT MIN(period) FROM forecast);
-- Q28 Repeat-customer opportunities and realized bookings.
SELECT c.customer_id,c.customer_name,COUNT(*) opportunities,SUM(CASE WHEN o.deal_status='Closed Won' THEN o.net_deal_value ELSE 0 END) bookings
FROM opportunities o JOIN customers c USING(customer_id) GROUP BY c.customer_id,c.customer_name HAVING COUNT(*)>1;
-- Q35 Largest policy-weighted forecast exposures; not an expected-loss estimate.
SELECT opportunity_id,weighted_value,risk_score,forecast_risk_value,risk_drivers FROM open_pipeline ORDER BY forecast_risk_value DESC LIMIT 50;
-- Q37 Stalled share of active pipeline count and value.
SELECT AVG(CASE WHEN deal_status='Stalled' THEN 1.0 ELSE 0 END) stalled_share,SUM(CASE WHEN deal_status='Stalled' THEN net_deal_value ELSE 0 END) stalled_value FROM open_pipeline;
-- Q38 No recent activity, joined to owner for follow-up.
SELECT o.opportunity_id,r.sales_rep_name,o.last_activity_date,o.next_follow_up_date FROM open_pipeline o JOIN sales_reps r USING(sales_rep_id) WHERE o.activity_gap_days>21;
-- Q40 Management attention queue ordered by exposure, preserving individual reasons.
SELECT opportunity_id,risk_level,risk_drivers,recommended_action,net_deal_value FROM open_pipeline WHERE risk_level IN ('High','Critical') ORDER BY risk_score DESC,net_deal_value DESC;
