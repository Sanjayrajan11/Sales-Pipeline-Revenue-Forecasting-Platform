"""MERIDIAN — an evidence-led revenue operations workspace."""

import logging
import sqlite3

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from database.database import DB, detail_events, read_table
from src.forecast import forecast
from src.funnel_analysis import funnel
from src.kpi_engine import kpis, target_analysis
from src.pipeline_analysis import compare, loss_pareto
from src.recommendations import recommendations
from src.scenario_engine import scenario
from src.utils import ACTIVE, ROOT, STAGES, config, csv_bytes, inr

PAGES = [
    "Command Center",
    "Pipeline Flow",
    "Revenue Outlook",
    "Opportunity Desk",
    "Opportunity Detail",
    "Sales Performance",
    "Funnel Diagnostics",
    "Customer & Market",
    "Scenario Lab",
    "Action Queue",
    "Data Explorer",
    "Methodology",
]
ACCENT = "#F5F5F5"

st.set_page_config(
    page_title="MERIDIAN | Revenue intelligence", layout="wide", initial_sidebar_state="collapsed"
)
st.markdown(
    """<style>
.block-container{max-width:1480px;padding-top:4.5rem;padding-bottom:3rem}
h1,h2,h3{font-family:Georgia,serif!important;letter-spacing:-.035em}
h1{font-size:3rem!important} h2{font-size:1.9rem!important}
[data-testid="stMetricValue"]{font-size:1.6rem;font-variant-numeric:tabular-nums}
[data-testid="stMetric"]{border-top:2px solid #e5e5e5;padding-top:.7rem}
[data-testid="stDataFrame"]{border:1px solid #3a3a3a}
[data-testid="stCaptionContainer"]{color:#dedede}
[data-testid="stAlert"],[data-testid="stMetricDelta"]{background:#202020;color:#fff}
.masthead{font-size:.78rem;letter-spacing:.23em;border-bottom:1px solid #3a3a3a;padding-bottom:.9rem;color:#fff}
.brief{font-family:Georgia,serif;font-size:1.3rem;line-height:1.5;border-left:3px solid #fff;padding:1rem 1.5rem;background:#161616;color:#fff;margin:1rem 0}
div[data-testid="stButton"] button{border-radius:3px}
@media(max-width:850px){.block-container{padding:4.5rem 1rem 1rem}h1{font-size:2rem!important}}
</style>""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load(stamp: float) -> tuple:
    """Invalidate snapshot when the database is atomically replaced."""
    return tuple(
        read_table(name)
        for name in ["opportunities", "stage_history", "sales_reps", "targets", "customers"]
    )


@st.cache_data(show_spinner="Recalculating forecast for this commercial scope…")
def scoped_forecast(o: pd.DataFrame, h: pd.DataFrame, t: pd.DataFrame, cfg: dict) -> tuple:
    """Cache a forecast by its actual inputs, not only widget labels."""
    return forecast(o, h, t, cfg)


def chart(fig: go.Figure) -> None:
    """Consistent understated visual language and legible INR axes."""
    # Plotly SVG titles do not wrap on phones; normal text preserves the full
    # business description at every viewport without shrinking chart labels.
    title = fig.layout.title.text
    if title:
        st.markdown(f"**{title}**")
    fig.update_layout(
        title_text=None,
        template="plotly_dark",
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="#FFFFFF"),
        colorway=[ACCENT, "#AAAAAA", "#777777", "#CCCCCC"],
        hoverlabel=dict(bgcolor="#202020", font_color="#FFFFFF"),
        margin=dict(l=12, r=12, t=12, b=25),
        height=370,
        legend=dict(orientation="h", y=-0.18),
    )
    fig.update_xaxes(gridcolor="#303030", zerolinecolor="#555555")
    fig.update_yaxes(gridcolor="#303030", zerolinecolor="#555555")
    st.plotly_chart(fig, width="stretch", theme=None, config={"displaylogo": False})


def money_chart(frame: pd.DataFrame, x: str, y: str, title: str) -> None:
    """Show compact lakh axes and exact INR tooltips."""
    frame = frame.copy()
    frame["value_inr"] = frame[y].map(inr)
    frame["INR lakh"] = frame[y] / 100000
    fig = px.bar(
        frame,
        x=x,
        y="INR lakh",
        title=title,
        custom_data=["value_inr"],
        color_discrete_sequence=[ACCENT],
    )
    fig.update_traces(hovertemplate="%{x}<br>%{customdata[0]}<extra></extra>")
    chart(fig)


def table(frame: pd.DataFrame, key: str, download: bool = True) -> None:
    """Display bounded tables with complete-result downloads and native sorting."""
    st.dataframe(frame.head(500), hide_index=True, width="stretch")
    if len(frame) > 500:
        st.caption(f"Showing 500 of {len(frame):,} rows. Download includes every matching row.")
    if download:
        st.download_button(
            "Download CSV",
            csv_bytes(frame),
            f"{key}.csv",
            "text/csv",
            key=f"download_{key}",
            on_click="ignore",
        )


def opportunity_view(o: pd.DataFrame, customers: pd.DataFrame, reps: pd.DataFrame) -> None:
    """Read an actual opportunity with indexed history and activity drill-down."""
    default = int(st.session_state.get("selected_opportunity", int(o.iloc[0].opportunity_id)))
    if "detail_id" not in st.session_state:
        st.session_state["detail_id"] = default
    wanted = st.number_input("Opportunity ID", min_value=1, step=1, key="detail_id")
    match = o[o.opportunity_id == wanted]
    if match.empty:
        st.warning(
            "This opportunity is outside the selected scope or was quarantined. Choose an ID from Opportunity Desk."
        )
        return
    r = match.iloc[0]
    st.subheader(f"Opportunity {int(r.opportunity_id):06d} · {r['product']}")
    customer = customers[customers.customer_id == r.customer_id].iloc[0]
    rep = reps[reps.sales_rep_id == r.sales_rep_id].iloc[0]
    st.write(f"{customer.customer_name} · {rep.sales_rep_name} · {r.region} · {r.industry}")
    a, b, c, d = st.columns(4)
    a.metric("Net contract value", inr(r.net_deal_value))
    b.metric("Stage", r.sales_stage)
    c.metric("Health / 100", "Closed" if pd.isna(r.health_score) else f"{r.health_score:.1f}")
    d.metric("Risk", f"{r.risk_level} · {int(r.risk_score)}")
    st.write(f"**Evidence:** {r.risk_drivers or 'No policy rule triggered'}")
    st.write(
        f"**Recommended next action:** {r.recommended_action or 'Maintain the agreed close plan'}"
    )
    st.caption(
        f"Forecast category: {r.forecast_category}. Weighted open contribution: {inr(r.weighted_value)}. Engagement: {r.engagement_score}/100. Expected close: {r.expected_close_date:%d %b %Y}."
    )
    visits, activities = detail_events(int(wanted))
    st.subheader("Deal timeline")
    visits["entry_date"] = pd.to_datetime(visits.entry_date)
    visits["observed_end"] = pd.to_datetime(visits.exit_date).fillna(
        pd.Timestamp(config()["as_of"])
    )
    chart(
        px.timeline(
            visits,
            x_start="entry_date",
            x_end="observed_end",
            y="sales_stage",
            title="Observed stage journey",
            color_discrete_sequence=[ACCENT],
        )
    )
    table(visits, "deal_stages")
    st.subheader("Activity history")
    table(activities, "deal_activities")
    with st.expander("Customer and opportunity record"):
        table(pd.DataFrame({"field": r.index, "value": r.astype(str).to_numpy()}), "deal_record")
        table(customer.to_frame("value").astype(str).reset_index(), "customer_record")
    with st.expander("Health contribution audit"):
        st.write(
            {
                name.replace("health_", ""): float(r[name])
                for name in o.columns
                if name.startswith("health_") and name not in ["health_score", "health_category"]
            }
        )


def main() -> None:
    """Render a complete application; errors retain a useful recovery message."""
    st.markdown(
        '<div class="masthead">MERIDIAN / REVENUE INTELLIGENCE / INDIA</div>',
        unsafe_allow_html=True,
    )
    cfg = config()
    if not DB.exists():
        st.warning("The analytical dataset is not ready. Run the pipeline, then refresh this page.")
        st.code("python run_pipeline.py\nstreamlit run app.py")
        return
    full, histories, reps, targets, customers = load(DB.stat().st_mtime)
    top1, top2 = st.columns([2, 3])
    with top1:
        page = st.selectbox("Workspace", PAGES, key="workspace")
    top2.caption(
        f"SYNTHETIC BUSINESS SIMULATION · SNAPSHOT {cfg['as_of']}\n\nAll monetary values are INR. “Revenue” means net booked contract value."
    )
    with st.expander("Commercial scope", expanded=False):
        controls = st.columns(4)
        region = controls[0].multiselect("Region", sorted(full.region.unique()), key="regions")
        team = controls[1].multiselect("Sales team", sorted(reps.team.unique()), key="teams")
        product = controls[2].multiselect(
            "Product", sorted(full["product"].unique()), key="products"
        )
        segment = controls[3].multiselect(
            "Customer segment", sorted(full.customer_segment.unique()), key="segments"
        )
        st.caption(
            "Empty selections mean all. Filters apply to every page. Date, stage, source and status filters are available in the record workspaces. Targets are not allocated to product or segment."
        )
    o = full.copy()
    if region:
        o = o[o.region.isin(region)]
    if team:
        o = o[o.sales_rep_id.isin(reps.loc[reps.team.isin(team), "sales_rep_id"])]
    if product:
        o = o[o["product"].isin(product)]
    if segment:
        o = o[o.customer_segment.isin(segment)]
    st.title(page)
    st.caption(
        f"{len(o):,} opportunities in scope · {cfg['history_start']} to {cfg['as_of']} · Scope uses creation history; calendar bookings use close dates."
    )
    if o.empty:
        st.info("No opportunities match these filters. Clear a selection in Commercial scope.")
        return
    h = histories[histories.opportunity_id.isin(o.opportunity_id)]
    t = targets.copy()
    if region:
        t = t[t.region.isin(region)]
    if team:
        t = t[t.sales_rep_id.isin(reps.loc[reps.team.isin(team), "sales_rep_id"])]
    allocated = not (product or segment)
    if not allocated:
        t = t.iloc[:0]
        st.info(
            "Product/segment quota is not allocated. Target comparisons are unavailable for this scope."
        )
    k = kpis(o)
    opened = o[o.deal_status.isin(ACTIVE)]
    if page == "Command Center":
        start = pd.Timestamp(cfg["as_of"]).replace(month=1, day=1)
        progress = target_analysis(o, t, start, pd.Timestamp(cfg["as_of"]))
        st.markdown(
            f'<div class="brief">The business briefing<br><b>{inr(k["open_pipeline"])}</b> of active pipeline. '
            f"<b>{k['stale_opportunity_rate']:.1%}</b> of open opportunities have had no activity for more than 21 days.</div>",
            unsafe_allow_html=True,
        )
        left, right = st.columns([3, 2])
        with left:
            st.subheader("01 / Revenue target progress")
            st.metric("Calendar year-to-date bookings", inr(progress["actual"]))
            if allocated:
                st.progress(
                    float(np.clip(progress["attainment"], 0, 1)),
                    text=f"{progress['attainment']:.1%} of elapsed-month target · {inr(progress['target'])}",
                )
                st.caption(
                    f"Remaining YTD target: {inr(progress['remaining_target'])}. Quotas are simulated planning inputs."
                )
            recent = o[o.created_date >= pd.Timestamp(cfg["as_of"]) - pd.Timedelta(days=89)].copy()
            recent["week"] = recent.created_date.dt.to_period("W").dt.start_time
            money_chart(
                recent.groupby("week", as_index=False).net_deal_value.sum(),
                "week",
                "net_deal_value",
                "Pipeline creation momentum · last 90 days",
            )
        with right:
            st.subheader("02 / Attention now")
            st.metric(
                "High / critical open deals",
                f"{opened.risk_level.isin(['High', 'Critical']).sum():,}",
            )
            st.metric("Top 10 pipeline concentration", f"{k['top10_pipeline_share']:.2%}")
            st.metric("Weighted pipeline · all close dates", inr(k["weighted_pipeline"]))
            f, _, _, _ = scoped_forecast(o, h, t, cfg)
            st.metric("Next 3 months · forecast", inr(f.head(3).forecast.sum()))
            if allocated:
                st.caption(
                    f"Forecast gap to target: {inr(f.head(3).target.sum() - f.head(3).forecast.sum())}"
                )
        st.subheader("03 / Management action queue")
        table(recommendations(o, h, cfg["as_of"], t).head(5), "briefing_actions")
        st.subheader("04 / Recent observed movement")
        table(
            h[h.exit_date.notna()].sort_values("exit_date", ascending=False).head(20),
            "recent_movement",
        )
    elif page == "Pipeline Flow":
        f = funnel(o, h)
        st.write(
            "Current stage lanes show inventory. Conversion below each lane uses completed historical transitions."
        )
        lane_cols = st.columns(3)
        for i, stage in enumerate(STAGES):
            subset = opened[opened.sales_stage == stage]
            row = f[f.stage == stage].iloc[0]
            with lane_cols[i % 3]:
                st.subheader(f"{i + 1:02d} / {stage}")
                st.metric(f"{len(subset):,} active deals", inr(subset.net_deal_value.sum()))
                st.caption(
                    f"Observed conversion {row.conversion:.1%} · drop-off {row.drop_off:.1%} · completed duration {row.average_days_completed:.1f} days"
                )
                if st.button(f"Explore {stage}", key=f"lane_{i}"):
                    st.session_state["lane_stage"] = stage
        selected = st.selectbox(
            "Stage records",
            STAGES,
            index=STAGES.index(st.session_state.get("lane_stage", "Lead")),
            key=f"lane_select_{st.session_state.get('lane_stage', 'Lead')}",
        )
        table(
            opened[opened.sales_stage == selected][
                [
                    "opportunity_id",
                    "customer_id",
                    "net_deal_value",
                    "days_in_current_stage",
                    "risk_level",
                    "recommended_action",
                ]
            ],
            "stage_records",
        )
    elif page == "Revenue Outlook":
        f, evaluation, backtest, actuals = scoped_forecast(o, h, t, cfg)
        st.caption(
            f"Selected forecast: {f.iloc[0].model}. Net bookings; future recognized revenue and cash collection are not modeled."
        )
        grain = st.radio("View", ["Monthly", "Quarterly", "Annual"], horizontal=True)
        frequency = {"Monthly": "M", "Quarterly": "Q", "Annual": "Y"}[grain]
        view = (
            f.assign(period=f.period.dt.to_period(frequency).astype(str))
            .groupby("period", as_index=False)[
                [
                    "forecast",
                    "lower",
                    "upper",
                    "pipeline_contribution",
                    "closed_won_contribution",
                    "target",
                ]
            ]
            .sum()
        )
        av = (
            actuals.assign(period=actuals.period.dt.to_period(frequency).astype(str))
            .groupby("period", as_index=False)[["actual", "target"]]
            .sum()
        )
        if grain != "Monthly":
            st.info(
                "Quarterly/annual totals cover only the displayed months; boundary periods may be partial. Summed range bounds are indicative, not calibrated aggregate intervals."
            )
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=av.period,
                y=av.actual / 100000,
                name="Actual bookings",
                line=dict(color="#AAAAAA"),
            )
        )
        fig.add_trace(
            go.Scatter(x=view.period, y=view.lower / 100000, line=dict(width=0), showlegend=False)
        )
        fig.add_trace(
            go.Scatter(
                x=view.period,
                y=view.upper / 100000,
                fill="tonexty",
                fillcolor="rgba(255,255,255,.16)",
                line=dict(width=0),
                name="Indicative range",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=view.period, y=view.forecast / 100000, name="Forecast", line=dict(color=ACCENT)
            )
        )
        if allocated:
            fig.add_trace(
                go.Scatter(
                    x=view.period,
                    y=view.target / 100000,
                    name="Target",
                    line=dict(color="#777", dash="dot"),
                )
            )
        fig.update_layout(
            yaxis_title="INR lakh", title="Revenue outlook · observed history and future bookings"
        )
        chart(fig)
        st.caption(
            "Range: validation residuals with horizon scaling. Not a guaranteed confidence interval. Forecast variance is undefined before actuals arrive."
        )
        a, b, c = st.columns(3)
        a.metric("Next 12 months · forecast", inr(f.forecast.sum()))
        b.metric("Pipeline due in forecast horizon", inr(f.pipeline_contribution.sum()))
        c.metric(
            "Target attainment",
            f"{f.forecast.sum() / f.target.sum():.1%}"
            if allocated and f.target.sum()
            else "Not allocated",
        )
        table(view if allocated else view.drop(columns="target"), "forecast_view")
        st.subheader("Commercial forecast categories")
        table(
            opened.groupby("forecast_category", as_index=False).agg(
                deals=("opportunity_id", "size"),
                gross_pipeline=("net_deal_value", "sum"),
                expected_bookings=("weighted_value", "sum"),
            ),
            "forecast_categories",
        )
        with st.expander("Backtest evidence and selection audit", expanded=True):
            table(evaluation, "forecast_evaluation")
            table(backtest[backtest.model == f.iloc[0].model], "forecast_origins")
            st.caption(
                "WAPE and MAPE are fractions. Model selection uses validation only. The later six months are held-out tests; one-month accuracy does not establish twelve-month accuracy."
            )
    elif page in ["Opportunity Desk", "Data Explorer"]:
        controls = st.columns(3)
        search = controls[0].text_input(
            "Search opportunity ID, customer ID or product", key=f"search_{page}"
        )
        statuses = controls[1].multiselect(
            "Deal status", sorted(o.deal_status.unique()), key=f"status_{page}"
        )
        sources = controls[2].multiselect(
            "Lead source", sorted(o.lead_source.unique()), key=f"source_{page}"
        )
        dates = st.date_input(
            "Created date range",
            (o.created_date.min().date(), o.created_date.max().date()),
            key=f"dates_{page}",
        )
        filtered = o.copy()
        if statuses:
            filtered = filtered[filtered.deal_status.isin(statuses)]
        if sources:
            filtered = filtered[filtered.lead_source.isin(sources)]
        if len(dates) != 2 or dates[0] > dates[1]:
            st.warning("Select a valid start and end date.")
            return
        filtered = filtered[
            filtered.created_date.between(pd.Timestamp(dates[0]), pd.Timestamp(dates[1]))
        ]
        if search:
            mask = (
                filtered[["opportunity_id", "customer_id", "product"]]
                .astype(str)
                .apply(lambda col: col.str.contains(search, case=False, regex=False))
                .any(axis=1)
            )
            filtered = filtered[mask]
        default_columns = [
            "opportunity_id",
            "customer_id",
            "sales_rep_id",
            "sales_stage",
            "net_deal_value",
            "expected_close_date",
            "total_opportunity_age_days",
            "health_score",
            "risk_level",
            "last_activity_date",
            "next_follow_up_date",
            "forecast_category",
        ]
        columns = st.multiselect(
            "Columns", list(o.columns), default=default_columns, key=f"cols_{page}"
        )
        sort = st.selectbox(
            "Sort by",
            ["net_deal_value", "risk_score", "created_date", "opportunity_id"],
            key=f"sort_{page}",
        )
        descending = st.checkbox("Descending", True, key=f"desc_{page}")
        filtered = filtered.sort_values(sort, ascending=not descending)
        st.caption(
            f"{len(filtered):,} matching records · total net opportunity value {inr(filtered.net_deal_value.sum())}"
        )
        if filtered.empty:
            st.info("No records match. Clear the search or change filters.")
        elif not columns:
            st.info("Choose at least one display column.")
        else:
            if page == "Opportunity Desk":
                st.caption(
                    "Select a table row to open its actual deal timeline below. Table headers also support sorting."
                )
                event = st.dataframe(
                    filtered[columns].head(500),
                    hide_index=True,
                    width="stretch",
                    on_select="rerun",
                    selection_mode="single-row",
                    key="desk_table",
                )
                if event.selection.rows:
                    chosen = int(filtered.iloc[event.selection.rows[0]].opportunity_id)
                    st.session_state["selected_opportunity"] = chosen
                    st.session_state["detail_id"] = chosen
                    opportunity_view(o, customers, reps)
                st.download_button(
                    "Download opportunities CSV",
                    csv_bytes(filtered[columns]),
                    "opportunities.csv",
                    "text/csv",
                    on_click="ignore",
                )
                st.caption(
                    "Table displays the first 500 matching rows. Export includes all matches."
                )
            else:
                table(filtered[columns], "explorer")
                with st.expander("Summary statistics", expanded=True):
                    table(
                        filtered[
                            [
                                "net_deal_value",
                                "engagement_score",
                                "total_opportunity_age_days",
                                "risk_score",
                            ]
                        ]
                        .describe()
                        .reset_index(),
                        "summary_statistics",
                    )
    elif page == "Opportunity Detail":
        opportunity_view(o, customers, reps)
    elif page == "Sales Performance":
        st.write(
            "Compare volume, conversion, cycle and quota together. These are simulated representatives, not personnel evaluations."
        )
        period = st.selectbox(
            "Booking period", ["Year to snapshot", "Last complete month", "Snapshot quarter"]
        )
        end = pd.Timestamp(cfg["as_of"])
        start = (
            end.replace(month=1, day=1)
            if period == "Year to snapshot"
            else (
                end.replace(day=1)
                if period == "Last complete month"
                else end.to_period("Q").start_time
            )
        )
        scope = o[(o.actual_close_date.between(start, end)) | o.deal_status.isin(ACTIVE)]
        perf = compare(scope, "sales_rep_id").merge(
            reps[["sales_rep_id", "sales_rep_name", "team"]], on="sales_rep_id"
        )
        quota = t[t.period.between(start, end)].groupby("sales_rep_id").target.sum()
        perf["period_quota"] = perf.sales_rep_id.map(quota)
        perf["attainment"] = perf.closed_won_revenue / perf.period_quota
        st.caption(
            "Resolved metrics use close dates within this period; active pipeline is the current snapshot. Snapshot-quarter quota covers elapsed months only here."
        )
        money_chart(
            perf,
            "sales_rep_name",
            "closed_won_revenue",
            "Bookings by representative · alongside multi-dimensional evidence",
        )
        table(
            perf[
                [
                    "sales_rep_name",
                    "team",
                    "period_quota",
                    "closed_won_revenue",
                    "attainment",
                    "open_pipeline",
                    "weighted_pipeline",
                    "win_rate",
                    "average_deal_size",
                    "average_sales_cycle",
                    "stale_opportunity_rate",
                    "closed_lost_value",
                ]
            ],
            "sales_performance",
        )
    elif page == "Funnel Diagnostics":
        f = funnel(o, h)
        st.write(
            "Where does the process lose potential bookings? Conversion denominators include only visits with an observed exit; pending visits remain visible."
        )
        chart(
            px.bar(
                f,
                x="stage",
                y=["advanced", "lost", "pending"],
                title="Stage entry outcomes",
                color_discrete_sequence=["#888888", ACCENT, "#BBBBBB"],
            )
        )
        table(f, "funnel_diagnostics")
        st.subheader("Lost-deal Pareto")
        dimension = st.selectbox(
            "Loss breakdown",
            ["lost_reason", "competitor_name", "industry", "region", "product", "lead_source"],
        )
        losses = loss_pareto(o, dimension)
        money_chart(losses, dimension, "lost_value", "Lost potential bookings · INR")
        table(losses, "loss_pareto")
        st.subheader("Sales-cycle distribution")
        won = o[o.deal_status.eq("Closed Won")]
        chart(
            px.histogram(
                won,
                x="sales_cycle_days",
                nbins=35,
                color_discrete_sequence=[ACCENT],
                title="Completed won cycles only; open deals are censored",
            )
        )
        st.write(
            {
                label: round(k[key], 1)
                for label, key in [
                    ("Mean days", "average_sales_cycle"),
                    ("Median days", "median_sales_cycle"),
                    ("P25", "cycle_p25"),
                    ("P75", "cycle_p75"),
                    ("P90", "cycle_p90"),
                ]
            }
        )
    elif page == "Customer & Market":
        dimension = st.selectbox(
            "Commercial dimension",
            [
                "industry",
                "region",
                "customer_segment",
                "product",
                "lead_source",
                "new_or_existing_customer",
                "company_size",
                "sales_rep_id",
            ],
        )
        g = compare(o, dimension)
        money_chart(
            g, dimension, "closed_won_revenue", "Commercial contribution · net won bookings"
        )
        table(
            g[
                [
                    dimension,
                    "opportunities",
                    "closed_won_revenue",
                    "win_rate",
                    "average_deal_size",
                    "average_sales_cycle",
                    "open_pipeline",
                    "weighted_pipeline",
                ]
            ],
            "market_comparison",
        )
        st.caption(
            "Differences are associations and include deal mix and cohort maturity. Product/segment targets are not fabricated."
        )
        st.subheader("Lead-source uncertainty")
        from src.statistics import statistical_analysis

        intervals, explanation = statistical_analysis(o)
        table(intervals, "source_intervals")
        with st.expander("Statistical assumptions and interpretation"):
            st.markdown(explanation)
    elif page == "Scenario Lab":
        st.write(
            "A 90-day pipeline sensitivity analysis. Changes are assumptions, not promised improvements or causal estimates."
        )
        cols = st.columns(3)
        win = cols[0].slider("Win probability adjustment (percentage points)", -30, 30, 0)
        size = cols[1].slider("Gross deal size adjustment (%)", -40, 50, 0)
        conversion = cols[2].slider("Executable conversion adjustment (%)", -40, 40, 0)
        cycle = cols[0].slider("Remaining sales-cycle adjustment (%)", -50, 50, 0)
        additional = cols[1].number_input("Additional opportunities", 0, 10000, 0, step=10)
        target_adjust = cols[2].slider("Target adjustment (%)", -50, 50, 0)
        discount = cols[0].slider("Discount adjustment (percentage points)", -15, 15, 0)
        future = (
            t[t.period > pd.Timestamp(cfg["as_of"])].groupby("period").target.sum().head(3).sum()
        )
        target = cols[1].number_input(
            "90-day planning target (INR)", min_value=0.0, value=float(future), step=100000.0
        )
        base = scenario(o, target, cfg["as_of"])
        changed = scenario(
            o,
            target,
            cfg["as_of"],
            win / 100,
            size / 100,
            conversion / 100,
            cycle / 100,
            int(additional),
            target_adjust / 100,
            discount / 100,
        )
        a, b, c = st.columns(3)
        a.metric(
            "Projected bookings",
            inr(changed["projected_revenue"]),
            inr(changed["projected_revenue"] - base["projected_revenue"]),
        )
        b.metric("Expected won deals", f"{changed['projected_won_deals']:,.1f}")
        c.metric(
            "Target attainment", f"{changed['target_attainment']:.1%}" if target else "No target"
        )
        result = pd.DataFrame(
            {
                "metric": list(base),
                "baseline": list(base.values()),
                "scenario": list(changed.values()),
            }
        )
        table(result, "scenario_comparison")
        st.caption(
            "Overdue deals have one remaining day. Cycle changes move eligibility across the 90-day boundary. Probability is clipped to [0,1], discount to [0,100%]. Added deals use the active cohort mean and assumed 90-day cycle. Planning target is explicitly editable because 90 days do not exactly equal three calendar months."
        )
    elif page == "Action Queue":
        actions = recommendations(o, h, cfg["as_of"], t)
        priorities = st.multiselect(
            "Priority", ["Critical", "High", "Medium"], default=["Critical", "High", "Medium"]
        )
        table(actions[actions.priority.isin(priorities)], "management_actions")
        st.subheader("Deal-level worklist")
        risk = st.multiselect(
            "Risk levels", ["Critical", "High", "Medium", "Low"], default=["Critical", "High"]
        )
        worklist = opened[opened.risk_level.isin(risk)].sort_values(
            ["risk_score", "net_deal_value"], ascending=False
        )
        table(
            worklist[
                [
                    "opportunity_id",
                    "sales_rep_id",
                    "net_deal_value",
                    "expected_close_date",
                    "risk_score",
                    "risk_level",
                    "risk_drivers",
                    "recommended_action",
                    "next_follow_up_date",
                ]
            ],
            "deal_actions",
        )
        st.caption(
            "Read-only decision support. Actions are recommendations; this application does not claim to update a CRM or send customer messages."
        )
    elif page == "Methodology":
        sections = [
            "METHODOLOGY.md",
            "KPI_DICTIONARY.md",
            "BUSINESS_RULES.md",
            "BUSINESS_REQUIREMENTS.md",
        ]
        doc = st.selectbox("Reference", sections)
        st.markdown((ROOT / "docs" / doc).read_text(encoding="utf-8"))
        st.subheader("Data quality audit")
        table(read_table("data_quality"), "quality_audit")
    st.divider()
    st.caption(
        f"View ready: {page} · MERIDIAN · Educational portfolio · All data is synthetic · INR net bookings · Decisions require real-world validation"
    )


try:
    main()
except (OSError, sqlite3.Error, ValueError, KeyError, pd.errors.DatabaseError) as exc:
    logging.exception("Application page failed")
    st.error(
        "This view could not load valid analytical data. Clear restrictive filters or rebuild the synthetic dataset using the command below. Other workspaces remain available."
    )
    st.code("python run_pipeline.py --regenerate")
    with st.expander("Diagnostic details"):
        st.write(str(exc))
