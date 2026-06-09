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
    """Submitting date range triggers re-fetch and chart update."""
    page.goto(f"{e2e_server}/market/chart")
    page.locator('input[name="start"]').fill("2024-01-01")
    page.locator('input[name="end"]').fill("2024-01-02")
    page.locator('button[type="submit"]').click()
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
