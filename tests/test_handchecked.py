"""Small independently hand-calculated acceptance examples for business formulas."""
import sqlite3

import numpy as np
import pandas as pd
import pytest

from src.funnel_analysis import funnel
from src.kpi_engine import kpis, target_analysis
from src.risk_engine import score
from src.scenario_engine import scenario


@pytest.fixture
def nine_deals():
    """Two wins, one loss, six active deals; all amounts are illustrative INR."""
    frame = pd.DataFrame({
        'opportunity_id': range(1, 10),
        'deal_status': ['Closed Won', 'Closed Won', 'Closed Lost', 'Open', 'Stalled', 'Open', 'Open', 'Open', 'Open'],
        'net_deal_value': [100., 300., 500., 200., 400., 50., 80., 120., 150.],
        'win_probability': [1., 1., 0., .5, .25, .2, .5, .75, .4],
        'sales_cycle_days': [10., 30., 20., np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        'activity_gap_days': [0, 0, 0, 22, 10, 0, 30, 40, 0],
        'total_opportunity_age_days': [10, 30, 20, 40, 60, 10, 90, 100, 50],
        'sales_stage': ['Closed Won', 'Closed Won', 'Closed Lost'] + ['Discovery'] * 6,
        'actual_close_date': pd.to_datetime(['2026-01-15', '2026-01-25', '2026-01-20'] + [None] * 6),
        'expected_close_date': pd.Timestamp('2026-01-31'),
        'next_follow_up_date': pd.Timestamp('2026-02-01'),
        'days_in_current_stage': 15, 'engagement_score': 80, 'competitor_present': False,
        'discount_percentage': 0., 'sales_rep_id': 1, 'customer_id': range(1, 10),
    })
    frame['opportunity_amount'] = frame.net_deal_value
    frame['weighted_value'] = (frame.net_deal_value * frame.win_probability).where(frame.deal_status.isin(['Open', 'Stalled']), 0)
    return frame


def test_handchecked_bookings_inventory_and_rates(nine_deals):
    result = kpis(nine_deals)
    expected = {'pipeline_value': 1900, 'closed_won_revenue': 400, 'closed_lost_value': 500,
                'open_pipeline': 1000, 'weighted_pipeline': 400, 'win_rate': 2/3,
                'average_deal_size': 200, 'median_deal_size': 200, 'average_sales_cycle': 20,
                'stale_opportunity_rate': .5, 'top5_pipeline_share': .95}
    for metric, value in expected.items():
        assert result[metric] == pytest.approx(value), metric


def test_handchecked_quota_and_coverage(nine_deals):
    targets = pd.DataFrame({'period': [pd.Timestamp('2026-01-01')], 'target': [1000.]})
    result = target_analysis(nine_deals, targets, pd.Timestamp('2026-01-01'), pd.Timestamp('2026-01-31'))
    assert result['remaining_target'] == 600
    assert result['pipeline_coverage'] == pytest.approx(1000/600)
    assert result['weighted_coverage'] == pytest.approx(400/600)
    assert result['attainment'] == .4


def test_handchecked_risk_and_health(nine_deals):
    result = score(nine_deals, '2026-01-31', [14, 18, 21, 18, 28, 21]).iloc[3]
    # Stale 15 + close-date pressure 10 + age 40 exceeds won-cycle P90=28: 10.
    assert result.risk_score == 35
    assert result.risk_level == 'Medium'
    assert set(result.risk_drivers.split('; ')) == {'No recent activity', 'Close date pressure', 'Long cycle'}
    # 6.25 + 3.3333 + 9.7222 + 10 + 12.5 + 6.25 + 12.5 + 12.5.
    assert result.health_score == 73.1


def test_handchecked_scenario(nine_deals):
    baseline = scenario(nine_deals, 1000, '2026-01-31')
    assert baseline['projected_revenue'] == 400
    changed = scenario(nine_deals, 1000, '2026-01-31', win_adjust=.1, deal_adjust=.1, discount_adjust=.05, target_adjust=.1)
    # (400 weighted + 1000 face * .1 probability uplift) * 1.1 size * .95 net.
    assert changed['projected_revenue'] == pytest.approx(522.5)
    assert changed['expected_pipeline'] == pytest.approx(1045)
    assert changed['projected_won_deals'] == pytest.approx(3.2)
    assert changed['revenue_gap'] == pytest.approx(577.5)
    assert changed['pipeline_required'] == pytest.approx(1155)


def test_handchecked_funnel_pending_denominator(nine_deals):
    opportunities = nine_deals.iloc[:3].copy()
    opportunities['deal_status'] = ['Closed Won', 'Closed Lost', 'Open']
    visits = pd.DataFrame({'opportunity_id': [1, 2, 3], 'sales_stage': 'Lead',
        'exit_date': pd.to_datetime(['2026-01-02', '2026-01-03', None]),
        'exit_to': ['Qualified', 'Closed Lost', ''], 'duration_days': [2, 4, 10]})
    lead = funnel(opportunities, visits).iloc[0]
    assert (lead.entered, lead.exited, lead.pending) == (3, 2, 1)
    assert lead.conversion == .5 and lead.drop_off == .5
    assert lead.average_days_completed == 3


def test_handchecked_revenue_growth_and_forecast_variance():
    with sqlite3.connect(':memory:') as con:
        pd.DataFrame({'period': ['2026-01', '2026-02', '2026-03'], 'actual': [100., 150., 120.], 'forecast': [110., 140., 120.]}).to_sql('months', con, index=False)
        rows = con.execute('SELECT actual / LAG(actual) OVER(ORDER BY period)-1, forecast-actual FROM months ORDER BY period').fetchall()
    assert rows[1][0] == .5
    assert rows[2][0] == pytest.approx(-.2)
    assert [r[1] for r in rows] == [10, -10, 0]


@pytest.mark.parametrize('override', [
    {'target': float('nan')}, {'additional': float('inf')},
    {'horizon_days': float('nan')}, {'additional': 1.5}, {'horizon_days': 1.5},
])
def test_scenario_rejects_invalid_planning_inputs(nine_deals, override):
    arguments = {'target': 1000, 'as_of': '2026-01-31', **override}
    with pytest.raises(ValueError):
        scenario(nine_deals, **arguments)
