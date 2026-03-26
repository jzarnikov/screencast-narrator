"""Element highlighting: draws animated highlights around Playwright locators."""

from __future__ import annotations

from screencast_narrator_client.shared_config import SharedConfig

_REMOVE_WRAPPER_JS = "document.getElementById('_e2e_multi_highlight')?.remove();"


def highlight(page, locators: list, config: SharedConfig) -> None:
    hl = config.highlight
    locators[0].evaluate(config.resolved_scroll_js)
    page.evaluate(config.resolved_scroll_wait_js)

    handles = [loc.element_handle() for loc in locators]
    page.evaluate(config.resolved_combine_js, handles)
    page.locator("#_e2e_multi_highlight").evaluate(config.resolved_draw_js)
    page.wait_for_timeout(hl.animation_speed_ms + hl.draw_wait_ms)

    page.evaluate(config.resolved_remove_js)
    page.evaluate(_REMOVE_WRAPPER_JS)
    page.wait_for_timeout(hl.remove_wait_ms)
