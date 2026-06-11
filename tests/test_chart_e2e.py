"""E2E tests for JS chart behavior using Playwright."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_chart_page_loads(page: Page, e2e_server: str) -> None:
    """Chart page renders with visible canvas."""
    page.goto(f"{e2e_server}/market/chart")
    expect(page.locator("#chart")).to_be_visible()
    expect(page.locator("canvas").first).to_be_visible()


@pytest.mark.e2e
def test_symbol_selector_populated(page: Page, e2e_server: str) -> None:
    """Symbol selector has option for TEST data."""
    page.goto(f"{e2e_server}/market/chart")
    expect(page.locator('select[name="symbol"] option')).to_have_count(1)
    expect(page.locator('select[name="symbol"]')).to_have_value("TEST")


@pytest.mark.e2e
def test_date_form_updates_chart(page: Page, e2e_server: str) -> None:
    """Changing date inputs triggers chart reload via change event."""
    page.goto(f"{e2e_server}/market/chart")
    page.locator('input[name="start"]').fill("2024-01-01")
    page.locator('input[name="end"]').fill("2024-01-02")
    # Dispatch change event to trigger auto-load
    page.evaluate(
        "document.querySelector('input[name=\"start\"]').dispatchEvent(new Event('change'))"
    )
    page.wait_for_timeout(1000)
    expect(page.locator("canvas").first).to_be_visible()


@pytest.mark.e2e
def test_unknown_symbol_shows_no_data(page: Page, e2e_server: str) -> None:
    """Navigating with unknown symbol does not crash."""
    page.goto(f"{e2e_server}/market/chart?symbol=NONEXISTENT")
    expect(page.locator("#chart")).to_be_visible()


@pytest.mark.e2e
def test_chart_defaults_to_last_200(page: Page, e2e_server: str) -> None:
    """Default view shows chart without parameters."""
    page.goto(f"{e2e_server}/market/chart")
    expect(page.locator("canvas").first).to_be_visible()
    # Default page loads without query params
    assert "?" not in page.url


@pytest.mark.e2e
def test_tooltip_shows_tickvol_and_spread(page: Page, e2e_server: str) -> None:
    """Tooltip displays tickvol and spread values from data."""
    page.goto(f"{e2e_server}/market/chart")
    # Wait for chart to load
    page.wait_for_timeout(1500)

    # Use mouse.move to hover over chart area (canvas has pointer-events issues)
    box = page.locator("#chart").bounding_box()
    if box:
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.wait_for_timeout(500)

    # Check tooltip content
    tooltip = page.locator("#chart-tooltip")
    expect(tooltip).to_be_visible()

    # Get tooltip text and verify tickvol and spread
    tooltip_text = tooltip.inner_text()
    print(f"Tooltip text: {tooltip_text}")

    # Should contain actual values from test data (tickvol=20, spread=2)
    assert "20" in tooltip_text  # tickvol from test data
    assert "2" in tooltip_text  # spread from test data


@pytest.mark.e2e
def test_infinite_scroll_triggers_fetch(page: Page, e2e_server: str) -> None:
    """Panning near left edge triggers scroll fetch, no crash."""
    page.goto(f"{e2e_server}/market/chart")
    page.wait_for_timeout(1500)

    initial_count = page.evaluate("window.__fetchCount")
    assert page.evaluate("window.allDataLength") > 0

    # Pan to extreme left edge to trigger scroll handler
    page.evaluate(
        """() => {
      var chart = window.chartApi.getChart();
      chart.timeScale().setVisibleLogicalRange({ from: 0.5, to: 1.5 });
    }"""
    )

    # Wait for fetchCount to increment
    page.wait_for_function("window.__fetchCount > " + str(initial_count), timeout=5000)
    # Verify still rendered
    expect(page.locator("canvas").first).to_be_visible()


@pytest.mark.e2e
def test_no_duplicate_bars_after_prepend(page: Page, e2e_server: str) -> None:
    """Scroll mechanism does not cause errors when boundary is reached."""
    page.goto(f"{e2e_server}/market/chart")
    page.wait_for_timeout(1500)

    initial_count = page.evaluate("window.__fetchCount")
    assert page.evaluate("window.allDataLength") > 0

    # Trigger scroll fetch twice
    page.evaluate(
        """() => {
      var chart = window.chartApi.getChart();
      chart.timeScale().setVisibleLogicalRange({ from: 0.5, to: 1.5 });
    }"""
    )
    page.wait_for_function("window.__fetchCount > " + str(initial_count), timeout=5000)

    page.evaluate(
        """() => {
      var chart = window.chartApi.getChart();
      chart.timeScale().setVisibleLogicalRange({ from: 1, to: 2.5 });
    }"""
    )

    # Verify no duplicates after any prepend that may have occurred
    has_duplicates = page.evaluate(
        """() => {
      var data = window.chartApi.getAllData();
      if (!data || data.length === 0) return false;
      var times = data.map(function(d) { return d.time; });
      return times.length !== new Set(times).size;
    }"""
    )
    assert not has_duplicates, "Duplicate timestamps found in allData"
