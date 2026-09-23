# Two-minute project explanation

I built MERIDIAN, a sales pipeline and revenue forecasting application for a simulated Indian B2B technology company. The business problem was that managers could see deal totals but could not easily tell which opportunities were progressing, which needed attention, or how much business might close.

I started with the business users: leadership, sales managers, representatives, finance and revenue operations. I documented their decisions, requirements, user stories and acceptance criteria, then mapped the current and proposed sales process. These were simulated requirements, not real company interviews.

I generated a reproducible dataset with 200,000 opportunities, customers, sales representatives, activities and stage histories. Deal values and outcomes depend on related business factors. I also introduced defects and built a cleaning pipeline that repairs fields from trusted source tables or quarantines invalid financial records.

I used Python and SQLite for the analytics and wrote 42 business SQL queries. A key distinction is that current pipeline is a snapshot, while funnel conversion needs actual stage transitions. I also separated won contract bookings from accounting-recognized revenue.

For forecasting, I compared simple historical methods and weighted-pipeline blends. I reconstructed historical cutoffs and separated model selection from held-out evaluation. I kept the risk engine rule-based so a user can see exactly why a deal needs attention.

The Streamlit application supports filters, record drill-down, exports and a scenario planner for assumptions such as win probability, discounts and timing. Recommendations show the observed evidence and an action, but I do not claim that they recovered revenue.

The strongest part of the project is connecting the business question to definitions, data, calculations and a usable application. The main limitation is that the data is synthetic, so real-world performance would need new validation.
