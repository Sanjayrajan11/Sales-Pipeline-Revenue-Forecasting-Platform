-- Q06 Resolved-deal win rate with an explicit closed-deal denominator.
SELECT SUM(CASE WHEN deal_status='Closed Won' THEN 1.0 ELSE 0 END)/NULLIF(SUM(CASE WHEN deal_status IN ('Closed Won','Closed Lost') THEN 1 ELSE 0 END),0) win_rate FROM opportunities;
-- Q10 Rep outcome mix; do not interpret volume-free win rate as a personnel score.
SELECT r.sales_rep_name,COUNT(*) cohort_count,SUM(CASE WHEN o.deal_status='Closed Won' THEN 1.0 ELSE 0 END)/NULLIF(SUM(CASE WHEN o.deal_status IN ('Closed Won','Closed Lost') THEN 1 ELSE 0 END),0) win_rate FROM opportunities o JOIN sales_reps r USING(sales_rep_id) GROUP BY r.sales_rep_id;
-- Q11 Open and weighted pipeline by sales representative.
SELECT r.sales_rep_name,COUNT(*) deals,SUM(o.net_deal_value) pipeline,SUM(o.weighted_value) weighted FROM open_pipeline o JOIN sales_reps r USING(sales_rep_id) GROUP BY r.sales_rep_id;
-- Q13 Regional year-to-snapshot target attainment, with matched monthly quotas.
WITH cutoff AS (SELECT DATE(MIN(period),'-1 day') d FROM forecast),
q AS (SELECT region,SUM(target) quota FROM targets WHERE period BETWEEN STRFTIME('%Y-01-01',(SELECT d FROM cutoff)) AND (SELECT d FROM cutoff) GROUP BY region),
a AS (SELECT region,SUM(net_deal_value) revenue FROM won_bookings WHERE actual_close_date BETWEEN STRFTIME('%Y-01-01',(SELECT d FROM cutoff)) AND (SELECT d FROM cutoff)||' 23:59:59' GROUP BY region)
SELECT q.region,q.quota,COALESCE(a.revenue,0) actual,COALESCE(a.revenue,0)/q.quota attainment FROM q LEFT JOIN a USING(region);
-- Q14 Lead-source quality: resolved win rate and average size alongside volume.
SELECT lead_source,COUNT(*) opportunities,AVG(net_deal_value) avg_size,SUM(CASE WHEN deal_status='Closed Won' THEN 1.0 ELSE 0 END)/NULLIF(SUM(CASE WHEN deal_status IN ('Closed Won','Closed Lost') THEN 1 ELSE 0 END),0) win_rate FROM opportunities GROUP BY lead_source;
-- Q26 Reps with above-average open value and below-company resolved conversion.
WITH performance AS (SELECT sales_rep_id,SUM(CASE WHEN deal_status IN ('Open','Stalled') THEN net_deal_value ELSE 0 END) pipeline,SUM(CASE WHEN deal_status='Closed Won' THEN 1.0 ELSE 0 END)/NULLIF(SUM(CASE WHEN deal_status IN ('Closed Won','Closed Lost') THEN 1 ELSE 0 END),0) win_rate FROM opportunities GROUP BY sales_rep_id)
SELECT * FROM performance WHERE pipeline>(SELECT AVG(pipeline) FROM performance) AND win_rate<(SELECT AVG(CASE WHEN deal_status='Closed Won' THEN 1.0 ELSE 0 END) FROM opportunities WHERE deal_status IN ('Closed Won','Closed Lost'));
-- Q36 Quarterly target attainment, preserving full-quarter target for partial quarters.
WITH q AS (SELECT STRFTIME('%Y',period)||'-Q'||CAST((CAST(STRFTIME('%m',period) AS INTEGER)+2)/3 AS INTEGER) quarter,SUM(target) quota FROM targets GROUP BY 1),
a AS (SELECT STRFTIME('%Y',actual_close_date)||'-Q'||CAST((CAST(STRFTIME('%m',actual_close_date) AS INTEGER)+2)/3 AS INTEGER) quarter,SUM(net_deal_value) revenue FROM won_bookings GROUP BY 1)
SELECT q.quarter,q.quota,COALESCE(a.revenue,0) revenue,COALESCE(a.revenue,0)/q.quota attainment FROM q LEFT JOIN a USING(quarter) ORDER BY q.quarter;
-- Q39 Top-three deal concentration per rep with windowed partitions.
WITH r AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY sales_rep_id ORDER BY net_deal_value DESC,opportunity_id) rn FROM open_pipeline)
SELECT sales_rep_id,SUM(CASE WHEN rn<=3 THEN net_deal_value ELSE 0 END)/SUM(net_deal_value) top3_share,COUNT(*) open_count FROM r GROUP BY sales_rep_id;
