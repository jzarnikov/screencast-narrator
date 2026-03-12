package screencastnarrator;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

import screencastnarrator.generated.ConfigSchema;
import screencastnarrator.generated.HighlightConfig;
import screencastnarrator.generated.HighlightStyle;
import screencastnarrator.generated.RecordingConfig;

public class SharedConfig {

    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static volatile SharedConfig instance;

    private final RecordingConfig recording;
    private final HighlightConfig highlight;

    private SharedConfig(RecordingConfig recording, HighlightConfig highlight) {
        this.recording = recording;
        this.highlight = highlight;
    }

    public RecordingConfig recording() {
        return recording;
    }

    public HighlightConfig highlight() {
        return highlight;
    }

    public static synchronized SharedConfig load() {
        if (instance != null) {
            return instance;
        }
        try (InputStream is = SharedConfig.class.getResourceAsStream("/common/config.json")) {
            if (is == null) {
                throw new IllegalStateException("common/config.json not found on classpath");
            }
            ConfigSchema schema = MAPPER.readValue(is, ConfigSchema.class);
            HighlightConfig hl = schema.getHighlight();
            hl.setScrollJs(resolveJs(hl.getScrollJs()));
            hl.setScrollWaitJs(resolveJs(hl.getScrollWaitJs()));
            hl.setDrawJs(resolveJs(hl.getDrawJs()));
            hl.setRemoveJs(resolveJs(hl.getRemoveJs()));
            instance = new SharedConfig(schema.getRecording(), hl);
            return instance;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public String resolvedDrawJs() {
        String result = highlight.getDrawJs();
        @SuppressWarnings("unchecked")
        Map<String, Object> fields = MAPPER.convertValue(highlight, Map.class);
        for (Map.Entry<String, Object> entry : fields.entrySet()) {
            result = result.replace("{{" + entry.getKey() + "}}", String.valueOf(entry.getValue()));
        }
        return result;
    }

    public List<String> ffmpegArgs(String outputFile) {
        RecordingConfig rec = recording;
        return List.of(
                "ffmpeg",
                "-loglevel", "error",
                "-f", "image2pipe",
                "-avioflags", "direct",
                "-fpsprobesize", "0",
                "-probesize", "32",
                "-analyzeduration", "0",
                "-c:v", "mjpeg",
                "-i", "pipe:0",
                "-y", "-an",
                "-r", String.valueOf(rec.getFps()),
                "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                "-c:v", rec.getCodec().value(),
                "-preset", rec.getPreset().value(),
                "-crf", String.valueOf(rec.getCrf()),
                "-pix_fmt", rec.getPixelFormat().value(),
                "-threads", "1",
                outputFile
        );
    }

    public SharedConfig withHighlightOverrides(HighlightStyle style) {
        HighlightStyle merged = HighlightStyles.merge(highlightStyleFromConfig(highlight), style);
        HighlightConfig overridden = new HighlightConfig(
                merged.getScrollWaitMs(),
                merged.getDrawDurationMs(),
                merged.getRemoveWaitMs(),
                merged.getColor(),
                merged.getPadding(),
                merged.getAnimationSpeedMs(),
                merged.getLineWidthMin(),
                merged.getLineWidthMax(),
                merged.getOpacity(),
                merged.getSegments(),
                merged.getCoverage(),
                highlight.getScrollJs(),
                highlight.getScrollWaitJs(),
                highlight.getDrawJs(),
                highlight.getRemoveJs()
        );
        return new SharedConfig(recording, overridden);
    }

    private static HighlightStyle highlightStyleFromConfig(HighlightConfig hl) {
        return new HighlightStyle(
                hl.getColor(),
                hl.getAnimationSpeedMs(),
                hl.getDrawWaitMs(),
                hl.getOpacity(),
                hl.getPadding(),
                hl.getScrollWaitMs(),
                hl.getRemoveWaitMs(),
                hl.getLineWidthMin(),
                hl.getLineWidthMax(),
                hl.getSegments(),
                hl.getCoverage()
        );
    }

    private static String resolveJs(String value) {
        if (!value.endsWith(".js")) return value;
        String resourcePath = "/common/" + value;
        try (InputStream js = SharedConfig.class.getResourceAsStream(resourcePath)) {
            if (js == null) {
                throw new IllegalStateException(resourcePath + " not found on classpath");
            }
            return new String(js.readAllBytes(), StandardCharsets.UTF_8).strip();
        } catch (IOException e) {
            throw new UncheckedIOException("Failed to read " + resourcePath, e);
        }
    }
}
