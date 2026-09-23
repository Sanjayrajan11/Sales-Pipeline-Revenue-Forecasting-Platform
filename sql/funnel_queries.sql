-- Q07 Stage conversion: resolved exits, not counts of current-stage inventory.
SELECT sales_stage,COUNT(*) entered,SUM(CASE WHEN exit_date IS NOT NULL THEN 1 ELSE 0 END) exited,
SUM(CASE WHEN exit_to NOT IN ('','Closed Lost') THEN 1.0 ELSE 0 END)/NULLIF(SUM(CASE WHEN exit_date IS NOT NULL THEN 1 ELSE 0 END),0) conversion FROM stage_history GROUP BY sales_stage ORDER BY MIN(stage_order);
-- Q08 Largest observed stage loss fraction, plus pending visits.
SELECT sales_stage,SUM(CASE WHEN exit_to='Closed Lost' THEN 1.0 ELSE 0 END)/NULLIF(SUM(CASE WHEN exit_date IS NOT NULL THEN 1 ELSE 0 END),0) drop_off,SUM(CASE WHEN exit_date IS NULL THEN 1 ELSE 0 END) pending FROM stage_history GROUP BY sales_stage ORDER BY drop_off DESC;
-- Q29 Completed stage duration and sample size.
SELECT sales_stage,AVG(duration_days) avg_days,COUNT(*) observed_exits FROM stage_history WHERE exit_date IS NOT NULL GROUP BY sales_stage ORDER BY MIN(stage_order);
-- Q30 Still-open visits: ages are right-censored, not completed duration estimates.
SELECT sales_stage,AVG(duration_days) average_current_age,MAX(duration_days) oldest_visit,COUNT(*) pending FROM stage_history WHERE exit_date IS NULL GROUP BY sales_stage ORDER BY average_current_age DESC;
-- Q31 Product conversion with observed closed counts.
SELECT product,SUM(CASE WHEN deal_status='Closed Won' THEN 1 ELSE 0 END) won,SUM(CASE WHEN deal_status='Closed Lost' THEN 1 ELSE 0 END) lost,AVG(CASE WHEN deal_status='Closed Won' THEN 1.0 WHEN deal_status='Closed Lost' THEN 0 END) win_rate FROM opportunities GROUP BY product;
-- Q42 Creation cohort outcomes, preserving pending counts to expose maturity bias.
SELECT STRFTIME('%Y-%m',created_date) cohort,COUNT(*) created,SUM(CASE WHEN deal_status='Closed Won' THEN 1 ELSE 0 END) won,SUM(CASE WHEN deal_status IN ('Open','Stalled') THEN 1 ELSE 0 END) pending,AVG(CASE WHEN deal_status='Closed Won' THEN 1.0 ELSE 0 END) observed_lead_to_win FROM opportunities GROUP BY 1 ORDER BY 1;
