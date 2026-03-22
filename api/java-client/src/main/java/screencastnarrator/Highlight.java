package screencastnarrator;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;

public class Highlight {

    private static final int ACK_POLLING_INTERVAL_MS = 40;

    private Highlight() {}

    public static void drawHighlight(Page page, Locator locator, SharedConfig config, CdpVideoRecorder recorder) {
        locator.evaluate(config.highlight().getScrollJs());
        page.evaluate(config.highlight().getScrollWaitJs());
        locator.evaluate(config.resolvedDrawJs());
        waitWithAcks(page, config.highlight().getAnimationSpeedMs() + config.highlight().getDrawWaitMs(), recorder);
    }

    public static void removeHighlight(Page page, SharedConfig config, CdpVideoRecorder recorder) {
        page.evaluate(config.highlight().getRemoveJs());
        waitWithAcks(page, config.highlight().getRemoveWaitMs(), recorder);
    }

    public static void highlight(Page page, Locator locator, SharedConfig config, CdpVideoRecorder recorder) {
        drawHighlight(page, locator, config, recorder);
        removeHighlight(page, config, recorder);
    }

    public static void highlight(Page page, Locator locator, SharedConfig config) {
        highlight(page, locator, config, null);
    }

    static void waitWithAcks(Page page, int totalMs, CdpVideoRecorder recorder) {
        if (recorder == null || totalMs <= 0) {
            page.waitForTimeout(totalMs);
            return;
        }
        int elapsed = 0;
        int interval = ACK_POLLING_INTERVAL_MS;
        while (elapsed < totalMs) {
            int wait = Math.min(interval, totalMs - elapsed);
            page.waitForTimeout(wait);
            elapsed += wait;
            recorder.ackLatestFrame();
        }
    }
}
