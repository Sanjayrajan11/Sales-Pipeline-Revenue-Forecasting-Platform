-- Q02 Closed-won booked contract value; not accounting-recognized revenue.
SELECT SUM(net_deal_value) booked_revenue FROM won_bookings;
-- Q03 Potential contract value lost.
SELECT SUM(net_deal_value) lost_value FROM opportunities WHERE deal_status='Closed Lost';
-- Q12 Revenue and tied rank across industries.
SELECT industry,SUM(net_deal_value) revenue,RANK() OVER(ORDER BY SUM(net_deal_value) DESC) revenue_rank FROM won_bookings GROUP BY industry;
-- Q15 Product booking mix.
SELECT product,COUNT(*) won_deals,SUM(net_deal_value) revenue FROM won_bookings GROUP BY product;
-- Q16 Average won deal size.
SELECT AVG(net_deal_value) average_won_deal FROM won_bookings;
-- Q17 Exact median in SQLite via two central row numbers.
WITH ordered AS (SELECT net_deal_value,ROW_NUMBER() OVER(ORDER BY net_deal_value) rn,COUNT(*) OVER() n FROM won_bookings)
SELECT AVG(net_deal_value) median_won_deal FROM ordered WHERE rn IN ((n+1)/2,(n+2)/2);
-- Q18 Won cycle percentiles: nearest-rank P25/P75/P90, explicitly not interpolation.
WITH ordered AS (SELECT sales_cycle_days,ROW_NUMBER() OVER(ORDER BY sales_cycle_days) rn,COUNT(*) OVER() n FROM won_bookings)
SELECT AVG(sales_cycle_days) avg_cycle,MIN(CASE WHEN rn>=n*.25 THEN sales_cycle_days END) p25,MIN(CASE WHEN rn>=n*.75 THEN sales_cycle_days END) p75,MIN(CASE WHEN rn>=n*.9 THEN sales_cycle_days END) p90 FROM ordered;
-- Q20 Lost-value Pareto: cumulative contribution by reason.
WITH reasons AS (SELECT lost_reason,SUM(net_deal_value) lost_value FROM opportunities WHERE deal_status='Closed Lost' GROUP BY lost_reason)
SELECT *,SUM(lost_value) OVER(ORDER BY lost_value DESC,lost_reason ROWS UNBOUNDED PRECEDING)/SUM(lost_value) OVER() cumulative_share FROM reasons ORDER BY lost_value DESC;
-- Q21 Calendar quarter booking growth. Final quarter may be partial, label in consumers.
WITH q AS (SELECT STRFTIME('%Y',actual_close_date)||'-Q'||CAST((CAST(STRFTIME('%m',actual_close_date) AS INTEGER)+2)/3 AS INTEGER) quarter,SUM(net_deal_value) revenue FROM won_bookings GROUP BY 1)
SELECT *,revenue/NULLIF(LAG(revenue) OVER(ORDER BY quarter),0)-1 growth FROM q;
-- Q27 Segments with valuable wins and long cycles; no causal interpretation.
SELECT customer_segment,AVG(net_deal_value) avg_won_size,AVG(sales_cycle_days) avg_won_cycle,COUNT(*) wins FROM won_bookings GROUP BY customer_segment;
-- Q32 Industry average deal size and deterministic dense rank.
SELECT industry,AVG(net_deal_value) avg_size,DENSE_RANK() OVER(ORDER BY AVG(net_deal_value) DESC) size_rank FROM opportunities GROUP BY industry;
-- Q33 Source contribution to total won bookings.
SELECT lead_source,SUM(net_deal_value) revenue,SUM(net_deal_value)/SUM(SUM(net_deal_value)) OVER() contribution FROM won_bookings GROUP BY lead_source;
-- Q34 Regional held-out one-month forecast error; selected regional models.
SELECT region,AVG(forecast-actual) bias,SUM(ABS(forecast-actual))/NULLIF(SUM(actual),0) wape FROM regional_backtest WHERE split='test' AND selected=1 GROUP BY region;
-- Q41 Rolling three complete monthly booking observations and next-month actual.
SELECT period,actual,AVG(actual) OVER(ORDER BY period ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) rolling3,LEAD(actual) OVER(ORDER BY period) next_actual FROM actuals ORDER BY period;
