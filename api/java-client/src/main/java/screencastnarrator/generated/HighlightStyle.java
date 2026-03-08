
package screencastnarrator.generated;

import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * User-customizable highlight appearance. All fields are optional — unset fields inherit from the shared config defaults.
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "color",
    "animationSpeedMs",
    "drawDurationMs",
    "opacity",
    "padding",
    "scrollWaitMs",
    "removeWaitMs",
    "lineWidthMin",
    "lineWidthMax",
    "segments",
    "coverage"
})
@Generated("jsonschema2pojo")
public class HighlightStyle {

    /**
     * CSS color for the highlight stroke (e.g. '#ff0000')
     * 
     */
    @JsonProperty("color")
    @JsonPropertyDescription("CSS color for the highlight stroke (e.g. '#ff0000')")
    private String color;
    /**
     * Duration of the draw animation in milliseconds
     * 
     */
    @JsonProperty("animationSpeedMs")
    @JsonPropertyDescription("Duration of the draw animation in milliseconds")
    private Integer animationSpeedMs;
    /**
     * How long the highlight stays visible after drawing
     * 
     */
    @JsonProperty("drawDurationMs")
    @JsonPropertyDescription("How long the highlight stays visible after drawing")
    private Integer drawDurationMs;
    /**
     * Opacity of the highlight stroke
     * 
     */
    @JsonProperty("opacity")
    @JsonPropertyDescription("Opacity of the highlight stroke")
    private Double opacity;
    /**
     * Padding around the element bounding box
     * 
     */
    @JsonProperty("padding")
    @JsonPropertyDescription("Padding around the element bounding box")
    private Integer padding;
    /**
     * Time to wait after scrolling the element into view
     * 
     */
    @JsonProperty("scrollWaitMs")
    @JsonPropertyDescription("Time to wait after scrolling the element into view")
    private Integer scrollWaitMs;
    /**
     * Time to wait after removing the highlight overlay
     * 
     */
    @JsonProperty("removeWaitMs")
    @JsonPropertyDescription("Time to wait after removing the highlight overlay")
    private Integer removeWaitMs;
    /**
     * Minimum stroke width of the hand-drawn highlight
     * 
     */
    @JsonProperty("lineWidthMin")
    @JsonPropertyDescription("Minimum stroke width of the hand-drawn highlight")
    private Integer lineWidthMin;
    /**
     * Maximum stroke width of the hand-drawn highlight
     * 
     */
    @JsonProperty("lineWidthMax")
    @JsonPropertyDescription("Maximum stroke width of the hand-drawn highlight")
    private Integer lineWidthMax;
    /**
     * Number of line segments in the hand-drawn rectangle
     * 
     */
    @JsonProperty("segments")
    @JsonPropertyDescription("Number of line segments in the hand-drawn rectangle")
    private Integer segments;
    /**
     * How much of the rectangle perimeter is drawn (0-1)
     * 
     */
    @JsonProperty("coverage")
    @JsonPropertyDescription("How much of the rectangle perimeter is drawn (0-1)")
    private Double coverage;

    /**
     * No args constructor for use in serialization
     * 
     */
    public HighlightStyle() {
    }

    /**
     * 
     * @param coverage
     *     How much of the rectangle perimeter is drawn (0-1).
     * @param padding
     *     Padding around the element bounding box.
     * @param color
     *     CSS color for the highlight stroke (e.g. '#ff0000').
     * @param scrollWaitMs
     *     Time to wait after scrolling the element into view.
     * @param animationSpeedMs
     *     Duration of the draw animation in milliseconds.
     * @param lineWidthMin
     *     Minimum stroke width of the hand-drawn highlight.
     * @param removeWaitMs
     *     Time to wait after removing the highlight overlay.
     * @param lineWidthMax
     *     Maximum stroke width of the hand-drawn highlight.
     * @param opacity
     *     Opacity of the highlight stroke.
     * @param drawDurationMs
     *     How long the highlight stays visible after drawing.
     * @param segments
     *     Number of line segments in the hand-drawn rectangle.
     */
    public HighlightStyle(String color, Integer animationSpeedMs, Integer drawDurationMs, Double opacity, Integer padding, Integer scrollWaitMs, Integer removeWaitMs, Integer lineWidthMin, Integer lineWidthMax, Integer segments, Double coverage) {
        super();
        this.color = color;
        this.animationSpeedMs = animationSpeedMs;
        this.drawDurationMs = drawDurationMs;
        this.opacity = opacity;
        this.padding = padding;
        this.scrollWaitMs = scrollWaitMs;
        this.removeWaitMs = removeWaitMs;
        this.lineWidthMin = lineWidthMin;
        this.lineWidthMax = lineWidthMax;
        this.segments = segments;
        this.coverage = coverage;
    }

    /**
     * CSS color for the highlight stroke (e.g. '#ff0000')
     * 
     */
    @JsonProperty("color")
    public String getColor() {
        return color;
    }

    /**
     * CSS color for the highlight stroke (e.g. '#ff0000')
     * 
     */
    @JsonProperty("color")
    public void setColor(String color) {
        this.color = color;
    }

    /**
     * Duration of the draw animation in milliseconds
     * 
     */
    @JsonProperty("animationSpeedMs")
    public Integer getAnimationSpeedMs() {
        return animationSpeedMs;
    }

    /**
     * Duration of the draw animation in milliseconds
     * 
     */
    @JsonProperty("animationSpeedMs")
    public void setAnimationSpeedMs(Integer animationSpeedMs) {
        this.animationSpeedMs = animationSpeedMs;
    }

    /**
     * How long the highlight stays visible after drawing
     * 
     */
    @JsonProperty("drawDurationMs")
    public Integer getDrawDurationMs() {
        return drawDurationMs;
    }

    /**
     * How long the highlight stays visible after drawing
     * 
     */
    @JsonProperty("drawDurationMs")
    public void setDrawDurationMs(Integer drawDurationMs) {
        this.drawDurationMs = drawDurationMs;
    }

    /**
     * Opacity of the highlight stroke
     * 
     */
    @JsonProperty("opacity")
    public Double getOpacity() {
        return opacity;
    }

    /**
     * Opacity of the highlight stroke
     * 
     */
    @JsonProperty("opacity")
    public void setOpacity(Double opacity) {
        this.opacity = opacity;
    }

    /**
     * Padding around the element bounding box
     * 
     */
    @JsonProperty("padding")
    public Integer getPadding() {
        return padding;
    }

    /**
     * Padding around the element bounding box
     * 
     */
    @JsonProperty("padding")
    public void setPadding(Integer padding) {
        this.padding = padding;
    }

    /**
     * Time to wait after scrolling the element into view
     * 
     */
    @JsonProperty("scrollWaitMs")
    public Integer getScrollWaitMs() {
        return scrollWaitMs;
    }

    /**
     * Time to wait after scrolling the element into view
     * 
     */
    @JsonProperty("scrollWaitMs")
    public void setScrollWaitMs(Integer scrollWaitMs) {
        this.scrollWaitMs = scrollWaitMs;
    }

    /**
     * Time to wait after removing the highlight overlay
     * 
     */
    @JsonProperty("removeWaitMs")
    public Integer getRemoveWaitMs() {
        return removeWaitMs;
    }

    /**
     * Time to wait after removing the highlight overlay
     * 
     */
    @JsonProperty("removeWaitMs")
    public void setRemoveWaitMs(Integer removeWaitMs) {
        this.removeWaitMs = removeWaitMs;
    }

    /**
     * Minimum stroke width of the hand-drawn highlight
     * 
     */
    @JsonProperty("lineWidthMin")
    public Integer getLineWidthMin() {
        return lineWidthMin;
    }

    /**
     * Minimum stroke width of the hand-drawn highlight
     * 
     */
    @JsonProperty("lineWidthMin")
    public void setLineWidthMin(Integer lineWidthMin) {
        this.lineWidthMin = lineWidthMin;
    }

    /**
     * Maximum stroke width of the hand-drawn highlight
     * 
     */
    @JsonProperty("lineWidthMax")
    public Integer getLineWidthMax() {
        return lineWidthMax;
    }

    /**
     * Maximum stroke width of the hand-drawn highlight
     * 
     */
    @JsonProperty("lineWidthMax")
    public void setLineWidthMax(Integer lineWidthMax) {
        this.lineWidthMax = lineWidthMax;
    }

    /**
     * Number of line segments in the hand-drawn rectangle
     * 
     */
    @JsonProperty("segments")
    public Integer getSegments() {
        return segments;
    }

    /**
     * Number of line segments in the hand-drawn rectangle
     * 
     */
    @JsonProperty("segments")
    public void setSegments(Integer segments) {
        this.segments = segments;
    }

    /**
     * How much of the rectangle perimeter is drawn (0-1)
     * 
     */
    @JsonProperty("coverage")
    public Double getCoverage() {
        return coverage;
    }

    /**
     * How much of the rectangle perimeter is drawn (0-1)
     * 
     */
    @JsonProperty("coverage")
    public void setCoverage(Double coverage) {
        this.coverage = coverage;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(HighlightStyle.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("color");
        sb.append('=');
        sb.append(((this.color == null)?"<null>":this.color));
        sb.append(',');
        sb.append("animationSpeedMs");
        sb.append('=');
        sb.append(((this.animationSpeedMs == null)?"<null>":this.animationSpeedMs));
        sb.append(',');
        sb.append("drawDurationMs");
        sb.append('=');
        sb.append(((this.drawDurationMs == null)?"<null>":this.drawDurationMs));
        sb.append(',');
        sb.append("opacity");
        sb.append('=');
        sb.append(((this.opacity == null)?"<null>":this.opacity));
        sb.append(',');
        sb.append("padding");
        sb.append('=');
        sb.append(((this.padding == null)?"<null>":this.padding));
        sb.append(',');
        sb.append("scrollWaitMs");
        sb.append('=');
        sb.append(((this.scrollWaitMs == null)?"<null>":this.scrollWaitMs));
        sb.append(',');
        sb.append("removeWaitMs");
        sb.append('=');
        sb.append(((this.removeWaitMs == null)?"<null>":this.removeWaitMs));
        sb.append(',');
        sb.append("lineWidthMin");
        sb.append('=');
        sb.append(((this.lineWidthMin == null)?"<null>":this.lineWidthMin));
        sb.append(',');
        sb.append("lineWidthMax");
        sb.append('=');
        sb.append(((this.lineWidthMax == null)?"<null>":this.lineWidthMax));
        sb.append(',');
        sb.append("segments");
        sb.append('=');
        sb.append(((this.segments == null)?"<null>":this.segments));
        sb.append(',');
        sb.append("coverage");
        sb.append('=');
        sb.append(((this.coverage == null)?"<null>":this.coverage));
        sb.append(',');
        if (sb.charAt((sb.length()- 1)) == ',') {
            sb.setCharAt((sb.length()- 1), ']');
        } else {
            sb.append(']');
        }
        return sb.toString();
    }

    @Override
    public int hashCode() {
        int result = 1;
        result = ((result* 31)+((this.coverage == null)? 0 :this.coverage.hashCode()));
        result = ((result* 31)+((this.padding == null)? 0 :this.padding.hashCode()));
        result = ((result* 31)+((this.color == null)? 0 :this.color.hashCode()));
        result = ((result* 31)+((this.scrollWaitMs == null)? 0 :this.scrollWaitMs.hashCode()));
        result = ((result* 31)+((this.animationSpeedMs == null)? 0 :this.animationSpeedMs.hashCode()));
        result = ((result* 31)+((this.lineWidthMin == null)? 0 :this.lineWidthMin.hashCode()));
        result = ((result* 31)+((this.removeWaitMs == null)? 0 :this.removeWaitMs.hashCode()));
        result = ((result* 31)+((this.lineWidthMax == null)? 0 :this.lineWidthMax.hashCode()));
        result = ((result* 31)+((this.opacity == null)? 0 :this.opacity.hashCode()));
        result = ((result* 31)+((this.drawDurationMs == null)? 0 :this.drawDurationMs.hashCode()));
        result = ((result* 31)+((this.segments == null)? 0 :this.segments.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof HighlightStyle) == false) {
            return false;
        }
        HighlightStyle rhs = ((HighlightStyle) other);
        return ((((((((((((this.coverage == rhs.coverage)||((this.coverage!= null)&&this.coverage.equals(rhs.coverage)))&&((this.padding == rhs.padding)||((this.padding!= null)&&this.padding.equals(rhs.padding))))&&((this.color == rhs.color)||((this.color!= null)&&this.color.equals(rhs.color))))&&((this.scrollWaitMs == rhs.scrollWaitMs)||((this.scrollWaitMs!= null)&&this.scrollWaitMs.equals(rhs.scrollWaitMs))))&&((this.animationSpeedMs == rhs.animationSpeedMs)||((this.animationSpeedMs!= null)&&this.animationSpeedMs.equals(rhs.animationSpeedMs))))&&((this.lineWidthMin == rhs.lineWidthMin)||((this.lineWidthMin!= null)&&this.lineWidthMin.equals(rhs.lineWidthMin))))&&((this.removeWaitMs == rhs.removeWaitMs)||((this.removeWaitMs!= null)&&this.removeWaitMs.equals(rhs.removeWaitMs))))&&((this.lineWidthMax == rhs.lineWidthMax)||((this.lineWidthMax!= null)&&this.lineWidthMax.equals(rhs.lineWidthMax))))&&((this.opacity == rhs.opacity)||((this.opacity!= null)&&this.opacity.equals(rhs.opacity))))&&((this.drawDurationMs == rhs.drawDurationMs)||((this.drawDurationMs!= null)&&this.drawDurationMs.equals(rhs.drawDurationMs))))&&((this.segments == rhs.segments)||((this.segments!= null)&&this.segments.equals(rhs.segments))));
    }

}
