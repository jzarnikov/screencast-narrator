package screencastnarrator;

import screencastnarrator.generated.HighlightStyle;

public final class HighlightStyles {

    private HighlightStyles() {}

    public static HighlightStyle merge(HighlightStyle base, HighlightStyle override) {
        return new HighlightStyle(
                override.getColor() != null ? override.getColor() : base.getColor(),
                override.getAnimationSpeedMs() != null ? override.getAnimationSpeedMs() : base.getAnimationSpeedMs(),
                override.getDrawDurationMs() != null ? override.getDrawDurationMs() : base.getDrawDurationMs(),
                override.getOpacity() != null ? override.getOpacity() : base.getOpacity(),
                override.getPadding() != null ? override.getPadding() : base.getPadding(),
                override.getScrollWaitMs() != null ? override.getScrollWaitMs() : base.getScrollWaitMs(),
                override.getRemoveWaitMs() != null ? override.getRemoveWaitMs() : base.getRemoveWaitMs(),
                override.getLineWidthMin() != null ? override.getLineWidthMin() : base.getLineWidthMin(),
                override.getLineWidthMax() != null ? override.getLineWidthMax() : base.getLineWidthMax(),
                override.getSegments() != null ? override.getSegments() : base.getSegments(),
                override.getCoverage() != null ? override.getCoverage() : base.getCoverage()
        );
    }

    public static SharedConfig.HighlightConfig applyTo(HighlightStyle style, SharedConfig.HighlightConfig config) {
        return new SharedConfig.HighlightConfig(
                style.getScrollWaitMs() != null ? style.getScrollWaitMs() : config.scrollWaitMs(),
                style.getDrawDurationMs() != null ? style.getDrawDurationMs() : config.drawWaitMs(),
                style.getRemoveWaitMs() != null ? style.getRemoveWaitMs() : config.removeWaitMs(),
                style.getColor() != null ? style.getColor() : config.color(),
                style.getPadding() != null ? style.getPadding() : config.padding(),
                style.getAnimationSpeedMs() != null ? style.getAnimationSpeedMs() : config.animationSpeedMs(),
                style.getLineWidthMin() != null ? style.getLineWidthMin() : config.lineWidthMin(),
                style.getLineWidthMax() != null ? style.getLineWidthMax() : config.lineWidthMax(),
                style.getOpacity() != null ? style.getOpacity() : config.opacity(),
                style.getSegments() != null ? style.getSegments() : config.segments(),
                style.getCoverage() != null ? style.getCoverage() : config.coverage(),
                config.scrollJs(),
                config.scrollWaitJs(),
                config.drawJs(),
                config.removeJs()
        );
    }
}
