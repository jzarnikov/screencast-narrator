package screencastnarrator;

import screencastnarrator.generated.SyncFrameStyle;

public final class SyncFrameStyles {

    private SyncFrameStyles() {}

    public static SyncFrameStyle merge(SyncFrameStyle base, SyncFrameStyle override) {
        return new SyncFrameStyle(
                override.getDisplayDurationMs() != null ? override.getDisplayDurationMs() : base.getDisplayDurationMs(),
                override.getPostRemovalGapMs() != null ? override.getPostRemovalGapMs() : base.getPostRemovalGapMs(),
                override.getDebugOverlay() != null ? override.getDebugOverlay() : base.getDebugOverlay(),
                override.getFontSize() != null ? override.getFontSize() : base.getFontSize()
        );
    }

    public static SharedConfig.SyncFrameConfig applyTo(SyncFrameStyle style, SharedConfig.SyncFrameConfig config) {
        return new SharedConfig.SyncFrameConfig(
                config.qrSize(),
                style.getDisplayDurationMs() != null ? style.getDisplayDurationMs() : config.displayDurationMs(),
                config.doneDisplayDurationMs(),
                style.getPostRemovalGapMs() != null ? style.getPostRemovalGapMs() : config.postRemovalGapMs(),
                config.backgroundColor(),
                config.injectJs(),
                config.removeJs()
        );
    }
}
