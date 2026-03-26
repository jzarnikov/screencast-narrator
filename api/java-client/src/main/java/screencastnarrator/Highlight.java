package screencastnarrator;

import com.microsoft.playwright.ElementHandle;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;

import java.util.Arrays;
import java.util.List;

public class Highlight {

    private static final int ACK_POLLING_INTERVAL_MS = 40;

    private static final String REMOVE_WRAPPER_JS = "document.getElementById('_e2e_multi_highlight')?.remove();";

    private Highlight() {}

    public static void highlight(Page page, Locator[] locators, SharedConfig config, CdpVideoRecorder recorder) {
        locators[0].evaluate(config.highlight().getScrollJs());
        page.evaluate(config.highlight().getScrollWaitJs());

        List<ElementHandle> handles = Arrays.stream(locators)
                .map(Locator::elementHandle)
                .toList();

        page.evaluate(config.highlight().getCombineJs(), handles);
        page.locator("#_e2e_multi_highlight").evaluate(config.resolvedDrawJs());
        waitWithAcks(page, config.highlight().getAnimationSpeedMs() + config.highlight().getDrawWaitMs(), recorder);

        page.evaluate(config.highlight().getRemoveJs());
        page.evaluate(REMOVE_WRAPPER_JS);
        waitWithAcks(page, config.highlight().getRemoveWaitMs(), recorder);
    }

    public static void highlight(Page page, Locator locator, SharedConfig config, CdpVideoRecorder recorder) {
        highlight(page, new Locator[]{locator}, config, recorder);
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
