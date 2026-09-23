# Power BI implementation guide

This is an implementation guide with DAX, not a fabricated .pbix deliverable. The runnable dashboard is Streamlit. Validate measures in Power BI after import; Desktop execution is not claimed.

## Import and model
Run `python scripts/export_powerbi.py` after the pipeline. Import generated CSV files from `data/processed/powerbi`. Currency columns use decimal/INR; dates are Date. Avoid loading raw duplicate/quarantined records. Export includes opportunity, activity, stage-visit, target, forecast and backtest facts plus conformed dimensions.

Use one-to-many, single-direction dimension→fact relationships. DimCustomer links customer_id; DimSalesRep links sales_rep_id; DimProduct links product_id; DimRegion links region; DimIndustry links industry; DimStage links sales_stage; DimLostReason links lost_reason. DimDate[Date] has an active relationship to FactOpportunities[created_date] and inactive relationship to [actual_close_date]. Use separate role-playing dimensions for expected close when users need simultaneous date slices. Targets link DimSalesRep and a month-start date; forecasts link month-start date. Do not connect activity directly to opportunity as a competing filter path: a dedicated DimOpportunity can filter both facts for drill-through. Keep account/customer paths unambiguous.

Quarter and year totals aggregate monthly forecasts only for months present. Clearly label partial years. Targets are rep-month, not product or segment; disable those target slicers or show an unallocated warning.

## DAX measures
The following examples assume imported table and field names from the exporter. For booking measures, deactivate creation-date filtering while activating close-date context. Forecast variance is meaningful only on completed backtest periods with actuals, so the example uses FactBacktest.

```dax
Pipeline Value = SUM(FactOpportunities[net_deal_value])

Closed Won Revenue =
CALCULATE(SUM(FactOpportunities[net_deal_value]),
  FactOpportunities[deal_status] = "Closed Won",
  CROSSFILTER(DimDate[Date], FactOpportunities[created_date], NONE),
  USERELATIONSHIP(DimDate[Date], FactOpportunities[actual_close_date]))

Won Count = CALCULATE(COUNTROWS(FactOpportunities), FactOpportunities[deal_status] = "Closed Won")
Resolved Count = CALCULATE(COUNTROWS(FactOpportunities), FactOpportunities[deal_status] IN {"Closed Won", "Closed Lost"})
Win Rate = DIVIDE([Won Count], [Resolved Count])

Open Pipeline = CALCULATE(SUM(FactOpportunities[net_deal_value]), FactOpportunities[deal_status] IN {"Open", "Stalled"})
Weighted Pipeline = SUM(FactOpportunities[weighted_value])
Average Deal Size = CALCULATE(AVERAGE(FactOpportunities[net_deal_value]), FactOpportunities[deal_status] = "Closed Won")
Average Sales Cycle = CALCULATE(AVERAGE(FactOpportunities[sales_cycle_days]), FactOpportunities[deal_status] = "Closed Won")
Target = SUM(FactTargets[target])
Remaining Target = MAX(0, [Target] - [Closed Won Revenue])

Period Due Pipeline =
CALCULATE([Open Pipeline],
  CROSSFILTER(DimDate[Date], FactOpportunities[created_date], NONE),
  USERELATIONSHIP(DimDate[Date], FactOpportunities[expected_close_date]))
Pipeline Coverage = DIVIDE([Period Due Pipeline], [Remaining Target])
Quota Attainment = DIVIDE([Closed Won Revenue], [Target])
Forecast Revenue = SUM(FactForecast[forecast])
Forecast Variance = SUM(FactBacktest[forecast]) - SUM(FactBacktest[actual])
Revenue Gap = [Target] - [Forecast Revenue]

Stale Opportunity Rate = DIVIDE(
  CALCULATE(COUNTROWS(FactOpportunities), FactOpportunities[deal_status] IN {"Open", "Stalled"}, FactOpportunities[activity_gap_days] > 21),
  CALCULATE(COUNTROWS(FactOpportunities), FactOpportunities[deal_status] IN {"Open", "Stalled"}))

Stage Conversion = DIVIDE(
  CALCULATE(COUNTROWS(FactStageVisits), FactStageVisits[exit_to] <> "Closed Lost", FactStageVisits[exit_date] <> BLANK()),
  CALCULATE(COUNTROWS(FactStageVisits), FactStageVisits[exit_date] <> BLANK()))

Previous Month Revenue = CALCULATE([Closed Won Revenue], DATEADD(DimDate[Date], -1, MONTH))
Revenue Growth = DIVIDE([Closed Won Revenue] - [Previous Month Revenue], [Previous Month Revenue])
```

Create the inactive expected-close relationship used above. Exported FactBacktest contains only the selected model, preventing accidental summation over nine candidates. On cohort pages use creation-date context; on revenue pages use the booking measures. On current snapshot pages avoid a date slicer that unintentionally restricts creation cohort. Format ratios as percentages and INR using an India locale.

## Pages and reconciliation
Reproduce the business briefing, transition diagnostics, forecast outlook, worklist and deal drill-through. Compare total value/won/open/weighted measures with reports/pipeline_kpis.csv. Compare transition counts with reports/funnel.csv and forecast totals with reports/forecast.csv. Test zero denominators, empty slicers, partial periods and product quota warnings. Never advertise Power BI execution until these checks are actually run in Desktop.
