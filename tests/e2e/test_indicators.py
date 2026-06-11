"""E2E tests for indicator overlay functionality using Playwright.

Tests cover adding indicators, verifying overlay rendering, and confirming
that active indicator configs survive page reload via localStorage.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_add_sma_overlay_renders(page: Page, e2e_server: str) -> None:
    """Adding SMA(20) creates an overlay row in the indicator panel."""
    page.goto(f"{e2e_server}/market/chart")

    # Wait for chart canvas to render (OHLCV data loaded)
    expect(page.locator("canvas").first).to_be_visible()

    # Wait for the indicator catalog to populate the select dropdown
    page.wait_for_function(
        "document.querySelectorAll('#indicator-select option').length > 1",
        timeout=5000,
    )

    # Select "SMA" from the indicator dropdown
    page.select_option("#indicator-select", "SMA")
    page.wait_for_timeout(200)

    # Click the Configure button to open the config form
    page.click("#indicator-config-btn")

    # Wait for the config form to render
    config_form = page.locator("#indicator-config-form")
    expect(config_form).to_be_visible()

    # The default timeperiod should already be 20; click Apply
    page.click(".indicator-submit-btn")

    # Wait for the overlay row to appear in the active indicators list
    overlay_row = page.locator(".indicator-row")
    expect(overlay_row.first).to_be_visible(timeout=5000)

    # Verify the overlay label shows SMA(20)
    expect(overlay_row.locator(".indicator-label")).to_contain_text("SMA(20)")


@pytest.mark.e2e
def test_localstorage_survives_reload(page: Page, e2e_server: str) -> None:
    """Active indicator configs persisted to localStorage survive page reload."""
    page.goto(f"{e2e_server}/market/chart")

    # Wait for chart and catalog
    expect(page.locator("canvas").first).to_be_visible()
    page.wait_for_function(
        "document.querySelectorAll('#indicator-select option').length > 1",
        timeout=5000,
    )

    # Add SMA(20) indicator
    page.select_option("#indicator-select", "SMA")
    page.wait_for_timeout(200)
    page.click("#indicator-config-btn")
    expect(page.locator("#indicator-config-form")).to_be_visible()
    page.click(".indicator-submit-btn")

    # Wait for overlay to render and confirm it's visible
    overlay_row = page.locator(".indicator-row")
    expect(overlay_row.first).to_be_visible(timeout=5000)

    # Reload the page
    page.reload()

    # Wait for chart to re-render
    expect(page.locator("canvas").first).to_be_visible()

    # Wait for restored overlay to appear via localStorage restore
    restored_row = page.locator(".indicator-row")
    expect(restored_row.first).to_be_visible(timeout=8000)

    # Verify the overlay label is still SMA(20)
    expect(restored_row.locator(".indicator-label")).to_contain_text("SMA(20)")
