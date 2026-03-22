/**
 * Record a narration that changes background colors with waits between.
 * Used by the e2e test to verify CDP captures frames across pauses.
 *
 * Usage:
 *     mvn -f examples/pom.xml compile exec:java \
 *         -Dexec.mainClass=RecordPauseTest \
 *         -Dexec.args="<output-dir> <html-path> [use-pause]"
 *
 * When "use-pause" is passed, uses sb.pause() instead of page.waitForTimeout().
 */

import com.microsoft.playwright.*;
import screencastnarrator.Storyboard;

import java.nio.file.Path;

public class RecordPauseTest {

    public static void main(String[] args) throws Exception {
        Path outputDir = Path.of(args[0]);
        String htmlPath = args[1];
        boolean usePause = args.length > 2 && "use-pause".equals(args[2]);

        try (Playwright pw = Playwright.create()) {
            Browser browser = pw.chromium().launch(new BrowserType.LaunchOptions().setHeadless(true));
            BrowserContext context = browser.newContext(new Browser.NewContextOptions()
                    .setViewportSize(1280, 720));
            Page page = context.newPage();

            page.navigate("file://" + htmlPath);
            page.waitForTimeout(500);

            Storyboard sb = new Storyboard(outputDir, page);

            sb.narrate("Color changes with waits between them.", sb2 -> {
                // Step 1: Red background
                page.evaluate("document.body.style.background = 'red'");
                if (usePause) sb2.pause(800); else page.waitForTimeout(800);

                // Step 2: Blue background after wait
                page.evaluate("document.body.style.background = 'blue'");
                if (usePause) sb2.pause(800); else page.waitForTimeout(800);

                // Step 3: Green background after another wait
                page.evaluate("document.body.style.background = 'green'");
                if (usePause) sb2.pause(800); else page.waitForTimeout(800);
            });

            sb.done();
            context.close();
            browser.close();
        }
    }
}
