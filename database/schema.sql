-- Analytics warehouse schema: pandas publishes typed tables; these constraints
-- enforce grain and indexes. Cross-table referential/financial checks run in validation.py.
CREATE UNIQUE INDEX IF NOT EXISTS pk_opportunity ON opportunities(opportunity_id);
CREATE UNIQUE INDEX IF NOT EXISTS pk_customer ON customers(customer_id);
CREATE UNIQUE INDEX IF NOT EXISTS pk_rep ON sales_reps(sales_rep_id);
CREATE UNIQUE INDEX IF NOT EXISTS pk_activity ON activities(activity_id);
CREATE UNIQUE INDEX IF NOT EXISTS pk_visit ON stage_history(transition_id);
CREATE UNIQUE INDEX IF NOT EXISTS pk_target ON targets(period, sales_rep_id);
CREATE INDEX IF NOT EXISTS ix_activity_opportunity ON activities(opportunity_id);
CREATE INDEX IF NOT EXISTS ix_history_opportunity ON stage_history(opportunity_id, entry_date);
CREATE INDEX IF NOT EXISTS ix_close ON opportunities(actual_close_date, deal_status);
CREATE INDEX IF NOT EXISTS ix_stage ON opportunities(sales_stage, deal_status);
CREATE INDEX IF NOT EXISTS ix_rep ON opportunities(sales_rep_id);
CREATE VIEW IF NOT EXISTS open_pipeline AS SELECT * FROM opportunities WHERE deal_status IN ('Open','Stalled');
CREATE VIEW IF NOT EXISTS won_bookings AS SELECT * FROM opportunities WHERE deal_status='Closed Won';
