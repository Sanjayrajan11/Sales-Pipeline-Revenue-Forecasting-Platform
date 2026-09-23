# Interview questions and answers

Answers describe this implementation without claiming real employment, stakeholder interviews or business impact.

## 1. Why did you choose this business problem?

Sales leaders must decide where to spend attention and whether expected bookings will meet quota. It connects requirements, SQL, data quality and decision support in one explainable workflow.

## 2. Who are the stakeholders?

Leadership, sales directors, managers, representatives, finance, revenue operations, business analysts and data analysts. Each has a different decision and level of detail.

## 3. How did you gather requirements?

I wrote a simulated stakeholder analysis and acceptance criteria. I did not conduct real company interviews. For a real engagement I would interview users, inspect CRM records and reconcile finance definitions.

## 4. What is the difference between pipeline and weighted pipeline?

Open pipeline adds the full net value of active deals. Weighted pipeline multiplies each active value by its historical stage-conditioned probability before adding.

## 5. How did you define win rate?

Won divided by won plus lost. Open and stalled outcomes are unresolved and excluded. Lead-to-win uses all created opportunities and answers a different question.

## 6. How did you calculate coverage?

Period-due open pipeline divided by the remaining target after period actuals. I return N/A if that remaining target is zero.

## 7. What makes an opportunity stale?

More than 21 days since its most recent activity at the snapshot. That is a visible policy assumption, not a proven universal threshold.

## 8. How did you calculate sales-cycle duration?

Actual close date minus creation date for closed opportunities. The primary cycle statistics use won deals. Active deal age is reported separately.

## 9. How did you forecast revenue?

I forecast net bookings using three simple historical baselines and two pipeline blend weights for each. Pipeline at each historical origin is reconstructed from dated events.

## 10. Why did you choose that approach?

It is explainable, inexpensive and can be compared against simple baselines. Model selection depends on validation results rather than the sophistication of an algorithm.

## 11. How did you validate the forecast?

I used six earlier rolling origins for model selection and six later origins as an untouched test. Each prediction uses information known before its target month.

## 12. What causes forecast variance?

Timing errors, conversion differences, unusually large contracts and changing deal mix can make bookings differ from the model. Signed error separates overforecasting from underforecasting.

## 13. How would you improve accuracy with real CRM data?

Preserve historical snapshots of dates, amounts and stages, record slips and reopenings, reconcile booked values and evaluate several horizons before adding complexity.

## 14. What is commit versus best case?

They are mutually exclusive confidence categories under explicit portfolio rules. Commit needs high stage probability, engagement and recency; best case has a lower probability threshold.

## 15. How would you resolve conflicting requirements?

Write down the decision, business value, cost and metric definition for each request. Agree a minimum shared scope and ask the accountable owner to resolve genuine policy tradeoffs.

## 16. How do you define acceptance criteria?

Describe observable behavior with a known input, action and expected outcome. For example, selecting a deal must return only events with that opportunity ID.

## 17. How did you identify bottlenecks?

I examined loss fractions among completed stage exits, pending volume and completed duration. A large current-stage count alone does not prove a bottleneck.

## 18. How would you measure recommendation success?

Establish a baseline, track follow-up completion, stale share and stage progression, and compare like-for-like cohorts prospectively. I do not claim recovery from a recommendation alone.

## 19. What would you change in production?

Add authenticated access, governed ingestion, historical CRM snapshots, automated monitoring, data ownership, deployment controls and business sign-off on metric definitions.

## 20. Why use SQLite?

It is portable and sufficient for a single-user local analytical portfolio. Indexed detail queries avoid loading all activity records for every drill-down.

## 21. What is the grain of opportunities?

One row per opportunity ID at the snapshot. Stage history is one stage visit and activities are individual dated interactions.

## 22. Why retain stage history?

Current stage cannot reveal previous transitions, early losses or duration. Dated visits also allow reconstruction of information at past forecast cutoffs.

## 23. What is a CTE?

A named intermediate result inside a SQL statement. I use it to make multi-step logic such as concentration and period growth readable.

## 24. How do window functions differ from GROUP BY?

GROUP BY collapses rows. Windows calculate over related rows while retaining row-level information, such as a rank or prior-period value.

## 25. When would you use ROW_NUMBER rather than RANK?

ROW_NUMBER assigns exactly one ordering position, useful for selecting exactly ten deals. RANK preserves ties and can skip subsequent ranks.

## 26. What does DENSE_RANK do?

It preserves ties but does not leave gaps. The industry average-size query demonstrates it.

## 27. Where did you use LAG and LEAD?

LAG provides prior-period value for growth; LEAD exposes the next observed month for a diagnostic comparison. Neither should leak into predictor inputs.

## 28. How did you compute median in SQLite?

Order won values using ROW_NUMBER, count all rows, then average the one or two middle values. The percentile query separately documents nearest-rank semantics.

## 29. Why use NULLIF in ratios?

It converts a zero denominator to NULL so SQL does not report an undefined ratio as a valid number. The UI labels unavailable ratios.

## 30. What is a cohort?

A group defined by a common entry condition, such as creation month. Recent cohorts have more unresolved deals, so their observed lead-to-win rates are not directly comparable to mature ones.

## 31. How did you generate realistic data?

I linked size to customer and product attributes and progression to engagement, competition, source, rep variation and timing. Probabilistic variation prevents perfect deterministic outcomes.

## 32. Why fix a random seed?

It allows another person to regenerate the same dataset and investigate differences caused by code changes rather than random changes.

## 33. How did you handle duplicates?

Injected opportunity and customer duplicates are exact copies with the same key. I keep the first and report removals. Conflicting duplicates in real data would require an explicit resolution policy.

## 34. How did you handle missing representatives?

The simulated account master contains an owner, which is the declared repair source. I do not invent a representative from an outcome.

## 35. Why quarantine some records?

An invalid amount or discount has no reliable independent repair source. Excluding it with a reason is more defensible than guessing a financial value.

## 36. What is an outlier versus an error?

An unusual but valid large deal should remain. Values outside declared valid bounds are flagged; invalid financial values are quarantined, and large valid deals receive concentration review.

## 37. How are Pandas and SQL used together?

Pandas handles generation, cleaning and analytical engines. SQLite stores a queryable warehouse and the SQL library independently expresses commercial questions.

## 38. Why vectorize Python operations?

Column operations are generally clearer and faster at this size than per-row mutation. Small loops remain appropriate for six stages, twelve forecast origins and reporting groups.

## 39. How do you prevent chained-assignment issues?

I use explicit copies and .loc assignments. Tests verify the resulting financial identities and repaired fields.

## 40. How do you handle empty filters?

The application detects an empty cohort and shows a recovery message before attempting charts or forecasts.

## 41. What does a confidence interval mean here?

Wilson intervals quantify uncertainty in a proportion under assumptions. Repeated customer and rep observations weaken independence, so I label the inference illustrative.

## 42. Why report effect size with a p-value?

A large dataset can make a tiny association statistically significant. Cramér V and booking value help judge whether a difference is worth investigating.

## 43. Does engagement cause higher conversion?

The synthetic generator encodes an association. Observational analysis alone cannot prove the causal effect of increasing engagement in a real company.

## 44. Why can MAPE be misleading?

It is undefined when actuals are zero and unstable near zero. WAPE aggregates absolute error relative to total actual value; MAPE is secondary with zero counts disclosed.

## 45. What is forecast bias?

The average signed prediction error. Positive means the model overpredicts bookings on average, even if absolute errors vary.

## 46. How did you prevent data leakage?

Historical training uses only outcomes closed before cutoff and stages entered before cutoff. Current final stages, current activity and risk scores are excluded from historical predictions.

## 47. Are your forecast intervals guaranteed?

No. They use six validation residuals and an explicit horizon-scaling heuristic. They are indicative ranges, not calibrated probability guarantees.

## 48. Why is bookings not recognized revenue?

A won contract may be recognized over service delivery or contract term and collected on another schedule. This dataset has no accounting ledger or collection schedule.

## 49. Why might a history-only forecast win?

Expected close dates can be noisy and pipeline probabilities describe eventual wins rather than exact timing. A simple aggregate history baseline may outperform a blend in validation.

## 50. How does the risk score work?

Ten visible rules add weighted points up to 100. The app shows triggered reasons and actions. The score is a prioritization policy rather than a loss probability.

## 51. How does health differ from risk?

Health adds eight positive components, including stage progress, recency, engagement and next action. Risk identifies specific policy breaches; they are not mathematical complements.

## 52. Why exclude closed deals from the worklist?

Their commercial outcome is already known. Treating them as current close-risk opportunities would waste attention and inflate exposure.

## 53. How does the scenario planner work?

It recomputes active-deal probability, net value and horizon eligibility under user assumptions. It compares the result with the same engine using zero adjustments.

## 54. Why separate win and conversion adjustments?

Win shifts the probability in percentage points; executable conversion scales the opportunity execution assumption. Both are sensitivity controls and may overlap conceptually, so users must not interpret them as independent causal estimates.

## 55. How does changing cycle affect a scenario?

It changes days remaining until expected close. Deals that move across the 90-day boundary become eligible or ineligible for projected bookings.

## 56. What does additional pipeline required mean?

The positive target shortfall divided by the scenario effective weighted conversion rate. If that rate is zero, the quantity is undefined rather than zero.

## 57. What Power BI model would you build?

Separate opportunity, activity, stage-visit and target facts with conformed customer, rep, product, date, region and stage dimensions. Avoid direct fact-to-fact relationships.

## 58. What is filter context in DAX?

It is the set of filters affecting a measure at evaluation time. CALCULATE changes that context, for example to count only Closed Won deals.

## 59. Why use DIVIDE in DAX?

It handles zero denominators and returns BLANK when a business ratio is undefined. That is safer than inventing zero.

## 60. How do you handle multiple dates in Power BI?

Use a date dimension with an active creation-date relationship and an inactive close-date relationship, or separate role-playing date dimensions. Booking measures activate close-date context explicitly.

## 61. How did you design the dashboard?

I organized it around decisions: a briefing, pipeline flow, outlook, record investigation, performance, scenarios and actions. Filters and period labels remain visible and consistent.

## 62. How did you make the UI accessible?

Controls have readable labels, risk includes explicit text, tables support keyboard interaction, and the palette uses white text on a black background with grayscale charts.

## 63. What do the tests prove?

They verify specific numerical contracts, invariants, leakage boundaries and UI states. They do not prove synthetic forecasts will work for a real company.

## 64. How do you explain the architecture?

A single pipeline generates and validates data, publishes SQLite, calculates analytics and reports, and a Streamlit app reads those outputs with interactive scoped calculations.

## 65. What is the biggest business limitation?

The requirements, behaviors and outcomes are simulated. There is no evidence yet that the proposed process changes would improve a real sales organization.

## 66. What is the biggest technical limitation?

The snapshot has no revised-date history, reopenings or recognition schedules. Long-horizon forecast quality and production multi-user behavior are not established.
