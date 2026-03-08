"""Shared helper: record a Wikipedia search iteration using Playwright + Storyboard."""

from __future__ import annotations

from screencast_narrator_client import Storyboard


def record_wikipedia_search(sb: Storyboard, page, iteration: int = 0) -> None:
    def navigate(s: Storyboard) -> None:
        def _nav(_s: Storyboard) -> None:
            page.goto("https://en.wikipedia.org", wait_until="load")
            page.wait_for_selector("input[name='search']", state="visible")
        s.screen_action(_nav, description="Navigate to Wikipedia")

    sb.narrate(navigate, text=f"Round {iteration + 1}. Navigating to Wikipedia.")

    def search(s: Storyboard) -> None:
        def _do(_s: Storyboard) -> None:
            box = page.locator("input[name='search']").first
            box.click()
            box.fill("")
            box.type("restaurant", delay=50)
            box.press("Enter")
            page.wait_for_selector("#firstHeading", state="visible")
            page.wait_for_selector("#mw-content-text h2", state="visible")
        s.screen_action(_do, description="Search for 'restaurant'")

    sb.narrate(search, text="Searching for restaurant.")

    headings = []
    for el in page.locator("#mw-content-text h2 .mw-headline, #mw-content-text h2").all()[:8]:
        try:
            text = el.inner_text(timeout=2000).replace("[edit]", "").strip()
            if text and text not in ("See also", "References", "External links", "Notes", "Further reading"):
                headings.append((text, el))
        except Exception:
            continue

    for heading_text, heading_el in headings[:3]:
        def highlight(s: Storyboard, _el=heading_el, _desc=heading_text) -> None:
            def _hl(_s: Storyboard) -> None:
                if _el is not None:
                    s.highlight(_el)
            s.screen_action(_hl, description=f"Highlight: {_desc}")

        sb.narrate(highlight, text=f"Section: {heading_text}.")
