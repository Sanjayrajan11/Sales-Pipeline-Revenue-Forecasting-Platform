# Business rules

BR01 Snapshot date is configured, never silently replaced with the machine date. This preserves reproducibility. Dataset size means opportunity rows before defect injection; stage/activity facts are additional.

BR02 Open pipeline includes Open and Stalled. Won/lost values partition the remainder. Closed opportunities have zero operational risk and no health score. Stale means activity gap >21 days; stalled is a generated/cleaned status at >30 days.

BR03 Eight equal health components each contribute up to 12.5 points: stage index/6; clipped 1−activity_gap/30; clipped 1−age/180; engagement/100; expected close not overdue; historical stage-conditioned conversion; clipped P90_size/deal_size; scheduled future next action. Total ≥70 Healthy, ≥45 Watch, otherwise At risk. Equal weights and thresholds are explicit portfolio policy assumptions, not empirically optimized business standards.

BR04 Risk points sum to 100 maximum: age>120 (10), activity gap>21 (15), expected close within 7 days or overdue (10), engagement<40 (10), stage age>1.5×policy limit (15), competitor (5), value>cohort P90 (10), discount>25% (5), missing/overdue follow-up (10), age>won-cycle P90 (10). Stage policy limits are configured as 14/18/21/18/28/21 days. Risk is Low<25, Medium25–44, High45–64, Critical65+. These are policy scores, not probabilities. Repeated stagnation cannot be inferred because this version records forward visits only; current-stage stagnation is the implemented signal.

BR05 Historical probabilities use resolved deals that reached each stage and were closed by the estimation cutoff, with Beta(1,1) smoothing: (wins+1)/(resolved+2). They estimate eventual win among resolved reaches, not the exact timing of close. Closed-only sampling can be biased.

BR06 Commit requires stage probability≥65%, engagement≥60 and activity gap≤14 days. Best Case requires probability≥40%; other active deals are Pipeline. Won has its own category; lost is Excluded. Categories are mutually exclusive, not nested subtotals. The forecast applies stage probability, not fixed arbitrary category multipliers.

BR07 Coverage uses pipeline whose expected close falls within the comparison period. Forecast snapshot scheduling moves overdue expected dates into the first forecast month. These different timing scopes are intentional and labelled. Future closed-won contribution is zero for future complete months. Current historical bookings are shown separately.

BR08 Scenario win changes are percentage points; size/cycle/target and executable conversion changes are relative percentages; discount changes are percentage points. Probability is clipped to [0,1]. Discount is clipped to [0,100%]. Dates are not randomly moved. Added opportunities assume current active-cohort average gross value, discount and probability with a 90-day initial cycle. A scenario is conditional arithmetic, not an estimated intervention effect.

BR09 Repair precedence: customer master for geography/industry; account manager for invalid rep; stage events for opportunity creation/current stage/close date; activity events for recency/counts; formula for net amount/cycle. Invalid unrecoverable gross amount or discount is quarantined with dependent events. Exact duplicate keys keep first. Customer lifetime value means accumulated observed won contract bookings, not predicted future CLV.

BR10 Quotas are available at representative-month and aggregate region/team level only. Product/segment filters disable quota comparisons. Full-quarter SQL targets and elapsed-quarter UI targets are labelled separately. All insights are computed on synthetic data and proposed actions require real-world validation.
