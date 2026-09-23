"""Read-only realism and reconciliation audit of the existing generated dataset."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from database.database import read_table
from src.kpi_engine import kpis
from src.pipeline_analysis import compare
from src.reporting import markdown_table
from src.utils import ROOT, config


def audit() -> None:
    """Report observed distributions without altering or fitting the synthetic source."""
    o = read_table('opportunities')
    h = read_table('stage_history')
    a = read_table('activities')
    targets = read_table('targets')
    cfg = config()
    assert o.opportunity_id.is_unique
    assert o.net_deal_value.gt(0).all()
    assert o.discount_percentage.between(0, 60).all()
    assert o.win_probability.between(0, 1).all()
    assert (o.actual_close_date.dropna() <= pd.Timestamp(cfg['as_of'])).all()
    dates = a.merge(o[['opportunity_id', 'created_date', 'actual_close_date']], on='opportunity_id', validate='many_to_one')
    assert (dates.activity_date >= dates.created_date).all()
    assert (dates.activity_date <= dates.actual_close_date.fillna(pd.Timestamp(cfg['as_of']))).all()
    for activity, stage in [('Product Demo', 'Demo'), ('Proposal', 'Proposal'), ('Negotiation', 'Negotiation'), ('Contract Review', 'Negotiation')]:
        selected = a[a.activity_type.eq(activity)]
        entry = h[h.sales_stage.eq(stage)].set_index('opportunity_id').entry_date
        assert (selected.activity_date >= selected.opportunity_id.map(entry)).all()
    measures = kpis(o)
    saved = read_table('pipeline_kpis').iloc[0]
    for name, value in measures.items():
        assert np.isclose(value, saved[name], rtol=1e-12, equal_nan=True), name
    b = read_table('backtest')
    selected_model = read_table('forecast').iloc[0].model
    heldout = b[b.model.eq(selected_model) & b.split.eq('test')]
    independent_wape = (heldout.forecast-heldout.actual).abs().sum()/heldout.actual.abs().sum()
    assert (b.cutoff < b.period).all()
    assert b[b.split.eq('validation')].period.max() < b[b.split.eq('test')].period.min()
    text = '# Data realism and reconciliation audit\n\nRead-only checks of the existing synthetic dataset; no regeneration or forced distribution adjustment.\n\n'
    numeric = o[['opportunity_amount', 'net_deal_value', 'discount_percentage', 'engagement_score', 'sales_cycle_days']].describe(percentiles=[.01, .25, .5, .75, .99]).round(2).reset_index()
    text += '## Financial and cycle distributions\n\n' + markdown_table(numeric) + '\n\nAmounts are INR; discount/engagement are percentage-point scales; cycles are days. Long tails are expected for enterprise contracts and remain visible rather than being removed merely for looking unusual.\n\n'
    text += '## Observed stages and outcomes\n\n' + markdown_table(o.groupby(['sales_stage', 'deal_status']).size().rename('count').reset_index()) + '\n\n'
    for dimension in ['region', 'industry', 'product', 'customer_segment', 'sales_rep_id']:
        g = compare(o, dimension)[[dimension, 'opportunities', 'win_rate', 'average_deal_size', 'average_sales_cycle', 'open_pipeline']].round(4)
        if dimension == 'sales_rep_id':
            start = pd.Timestamp(cfg['as_of']).replace(month=1, day=1)
            won = o[o.deal_status.eq('Closed Won') & o.actual_close_date.between(start, cfg['as_of'])]
            actual = won.groupby('sales_rep_id').net_deal_value.sum()
            quota = targets[targets.period.between(start, cfg['as_of'])].groupby('sales_rep_id').target.sum()
            g['ytd_attainment'] = g.sales_rep_id.map(actual)/g.sales_rep_id.map(quota)
        text += f'## Variation by {dimension}\n\n' + markdown_table(g) + '\n\n'
    text += f'## Integrity and temporal checks\n\n- {len(o):,} unique clean opportunities, {len(a):,} activities and {len(h):,} stage visits inspected.\n- Every activity falls within its opportunity lifetime. Advanced activities occur only after the relevant stage entry.\n- All stored cohort KPIs independently reconcile to the underlying records.\n- Validation precedes held-out test; all backtest cutoffs precede forecast periods.\n- Independently recomputed selected-model held-out WAPE: {independent_wape:.6%}.\n- Future-outcome mutation regression tests verify that later statuses/stages do not affect earlier snapshot predictions.\n\n'
    text += '## Interpretation and limitations\n\nThe observed deal values, discount range, imperfect win rates, cycle dispersion and differences between representatives are plausible for this simulated commercial scale. This is a structural sanity audit, not calibration against a real Indian company. Quotas are planning assumptions. Forward-only stage visits, one account per customer, immutable initial expected dates and full-contract bookings simplify the process. No distribution was modified during this audit.\n'
    (ROOT/'reports/data_realism_audit.md').write_text(text, encoding='utf-8')
    hashes = {}
    for path in sorted((ROOT/'data/raw').glob('*')):
        if path.is_file():
            with path.open('rb') as handle:
                hashes[path.relative_to(ROOT).as_posix()] = hashlib.file_digest(handle, 'sha256').hexdigest()
    (ROOT/'reports/raw_data_hashes.json').write_text(json.dumps(hashes, indent=2), encoding='utf-8')
    print(f'Data audit passed: {len(o):,} opportunities; {len(a):,} activities; {len(h):,} stage visits; held-out WAPE {independent_wape:.4%}.')


if __name__ == '__main__':
    audit()
