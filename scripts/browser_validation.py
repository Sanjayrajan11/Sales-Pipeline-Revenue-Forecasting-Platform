"""Exercise the running localhost app in installed Google Chrome via Playwright."""

import csv
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
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


def run() -> None:
    """Save real Chrome screenshots and a machine-readable interaction audit."""
    evidence = []
    expect.set_options(timeout=90000)
    downloads = ROOT / "data/processed/browser_downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 1000}, accept_downloads=True
        )
        page = context.new_page()
        page.set_default_timeout(90000)
        page.goto("http://localhost:8501", wait_until="domcontentloaded")

        def ready(name: str) -> None:
            expect(page.get_by_role("heading", name=name, exact=True)).to_be_visible()
            expect(page.get_by_text(f"View ready: {name} · MERIDIAN", exact=False)).to_be_attached()
            page.get_by_role("button", name="Stop", exact=True).wait_for(
                state="hidden", timeout=90000
            )
            expect(page.get_by_test_id("stException")).to_have_count(0)
            expect(page.get_by_test_id("stAlert").filter(has_text="default value but also had its value set")).to_have_count(0)
            expect(
                page.get_by_test_id("stAlert").filter(has_text="This view could not load")
            ).to_have_count(0)

        def navigate(name: str) -> None:
            page.get_by_role("button", name="Stop", exact=True).wait_for(
                state="hidden", timeout=90000
            )
            select = page.get_by_role("combobox", name="Workspace", exact=True)
            select.click()
            select.fill(name)
            page.get_by_role("option", name=name, exact=True).click()
            ready(name)

        ready("Command Center")
        for name in PAGES:
            if name != "Command Center":
                navigate(name)
            path = (
                ROOT / "screenshots" / (name.lower().replace(" & ", "-").replace(" ", "-") + ".png")
            )
            page.screenshot(path=str(path), full_page=True)
            evidence.append(
                {
                    "check": name,
                    "result": "loaded without application errors",
                    "screenshot": path.relative_to(ROOT).as_posix(),
                }
            )
            print("Chrome page OK:", name, flush=True)

        navigate("Scenario Lab")
        metric = page.get_by_test_id("stMetricValue").first
        before = metric.inner_text()
        slider = page.locator(
            'input[type="range"][aria-label="Win probability adjustment (percentage points)"]'
        )
        slider.focus()
        slider.press("ArrowRight")
        expect(metric).not_to_have_text(before)
        after = metric.inner_text()
        evidence.append(
            {"check": "Scenario change", "before": before, "after": after, "result": "changed"}
        )
        with page.expect_download() as info:
            page.get_by_role("button", name="Download CSV", exact=True).click()
        download = info.value
        download.save_as(str(downloads / "scenario-download.csv"))
        with (downloads / "scenario-download.csv").open(encoding="utf-8-sig") as handle:
            records = list(csv.DictReader(handle))
        assert len(records) == 9 and {"metric", "baseline", "scenario"} == set(records[0])
        print("Chrome interaction OK: scenario and download", flush=True)
        evidence.append(
            {
                "check": "Scenario CSV download",
                "rows": len(records),
                "result": "parsed and validated",
            }
        )

        navigate("Pipeline Flow")
        page.get_by_role("button", name="Explore Proposal", exact=True).click()
        expect(page.get_by_role("combobox", name="Stage records", exact=True)).to_have_value(
            "Proposal"
        )
        evidence.append({"check": "Stage lane button", "result": "Proposal records selected"})
        print("Chrome interaction OK: stage lane", flush=True)

        navigate("Data Explorer")
        search = page.get_by_role(
            "textbox", name="Search opportunity ID, customer ID or product", exact=True
        )
        search.fill("no-such-record-xyz")
        search.press("Enter")
        expect(
            page.get_by_text("No records match. Clear the search or change filters.", exact=True)
        ).to_be_visible()
        search.fill("Workflow Suite")
        search.press("Enter")
        expect(
            page.get_by_text("No records match. Clear the search or change filters.", exact=True)
        ).to_have_count(0)
        descending = page.get_by_role("checkbox", name="Descending", exact=True)
        descending.focus()
        descending.press("Space")
        expect(descending).not_to_be_checked()
        # Widget state changes immediately; allow the websocket rerun to start
        # before checking that the server has finished replacing download data.
        page.wait_for_timeout(1000)
        ready("Data Explorer")
        with page.expect_download() as info:
            page.get_by_role("button", name="Download CSV", exact=True).first.click()
        info.value.save_as(str(downloads / "explorer-download.csv"))
        with (downloads / "explorer-download.csv").open(encoding="utf-8-sig") as handle:
            exported = list(csv.DictReader(handle))
        assert len(exported) > 500
        assert float(exported[0]["net_deal_value"]) <= float(exported[-1]["net_deal_value"])
        print("Chrome interaction OK: explorer search/sort/export", flush=True)
        evidence.append(
            {
                "check": "Explorer search, sorting, full CSV export",
                "rows": len(exported),
                "result": "passed",
            }
        )

        navigate("Opportunity Desk")
        # The Streamlit data grid is canvas-rendered but exposes selectable rows.
        grid = page.get_by_test_id("stDataFrame").first
        grid.scroll_into_view_if_needed()
        # Glide's transparent scroller receives pointer input over the canvas.
        grid.locator(".dvn-scroller").click(position={"x": 18, "y": 55})
        expect(page.get_by_role("heading", name="Deal timeline", exact=True)).to_be_visible()
        print("Chrome interaction OK: opportunity drill-down", flush=True)
        evidence.append(
            {"check": "Opportunity row drill-down", "result": "actual timeline displayed"}
        )

        navigate("Revenue Outlook")
        page.get_by_text("Quarterly", exact=True).click()
        expect(page.get_by_text("Quarterly/annual totals cover only", exact=False)).to_be_visible()
        page.get_by_text("Annual", exact=True).click()
        expect(page.get_by_role("radio", name="Annual", exact=True)).to_be_checked()
        page.wait_for_timeout(1000)
        ready("Revenue Outlook")
        evidence.append({"check": "Forecast quarterly and annual views", "result": "passed"})

        navigate("Command Center")
        page.get_by_text("Commercial scope", exact=True).click()
        page.wait_for_timeout(1000)
        ready("Command Center")
        before = page.get_by_test_id("stMetricValue").first.inner_text()
        region = page.get_by_role("combobox", name="Region", exact=True)
        region.click()
        region.fill("North")
        page.get_by_role("option", name="North", exact=True).click()
        region.press("Escape")
        expect(page.get_by_test_id("stMetricValue").first).not_to_have_text(before)
        evidence.append({"check": "Global region filter", "result": "bookings recalculated"})
        page.get_by_role("button", name="Remove North", exact=True).click()
        page.wait_for_timeout(1000)
        ready("Command Center")
        page.get_by_text("Commercial scope", exact=True).click()
        page.wait_for_timeout(1000)
        ready("Command Center")
        for width in [1280, 820, 390]:
            page.set_viewport_size({"width": width, "height": 1000})
            for name in PAGES:
                navigate(name)
                overflow = page.evaluate("""() => {
                    const main = document.querySelector('[data-testid="stMain"]');
                    return document.documentElement.scrollWidth > window.innerWidth ||
                        (main && main.scrollWidth > main.clientWidth + 1);
                }""")
                assert not overflow, f"Horizontal viewport overflow: {name} at {width}"
                path = ROOT / "screenshots" / f"{name.lower().replace(' ', '-')}-{width}.png"
                page.screenshot(path=str(path), full_page=True)
                if width == 390:
                    charts = page.get_by_test_id("stPlotlyChart")
                    for index in range(charts.count()):
                        chart = charts.nth(index)
                        chart.scroll_into_view_if_needed()
                        expect(chart.locator(".js-plotly-plot")).to_have_count(1)
                        assert chart.locator(".js-plotly-plot").evaluate(
                            "el => el._fullData && el._fullData.length > 0"
                        ), f"Blank chart: {name} #{index + 1}"
                    page.get_by_text(f"View ready: {name} · MERIDIAN", exact=False).scroll_into_view_if_needed()
                    page.screenshot(path=str(path.with_stem(path.stem + '-bottom')), full_page=True)
                evidence.append(
                    {"check": f"{name} at {width}px", "result": "no page-level horizontal overflow"}
                )
                print(f"Chrome responsive OK: {name} at {width}px", flush=True)
        report = {
            "browser": "Installed Google Chrome",
            "version": browser.version,
            "checks": evidence,
        }
        (ROOT / "reports/browser_validation.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        context.close()
        browser.close()
        print(f"Chrome validation completed: {len(evidence)} checks.", flush=True)


if __name__ == "__main__":
    run()
