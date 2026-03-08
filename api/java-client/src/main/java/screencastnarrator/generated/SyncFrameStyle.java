
package screencastnarrator.generated;

import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * User-customizable sync frame timing and overlay settings. All fields are optional — unset fields inherit from the shared config defaults.
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "displayDurationMs",
    "postRemovalGapMs",
    "debugOverlay",
    "fontSize"
})
@Generated("jsonschema2pojo")
public class SyncFrameStyle {

    /**
     * How long the green QR overlay is shown per frame (default 160ms = ~4 frames at 25fps)
     * 
     */
    @JsonProperty("displayDurationMs")
    @JsonPropertyDescription("How long the green QR overlay is shown per frame (default 160ms = ~4 frames at 25fps)")
    private Integer displayDurationMs;
    /**
     * Gap after removing the overlay before the next action (default 80ms)
     * 
     */
    @JsonProperty("postRemovalGapMs")
    @JsonPropertyDescription("Gap after removing the overlay before the next action (default 80ms)")
    private Integer postRemovalGapMs;
    /**
     * Show narration text as subtitle overlay during recording
     * 
     */
    @JsonProperty("debugOverlay")
    @JsonPropertyDescription("Show narration text as subtitle overlay during recording")
    private Boolean debugOverlay;
    /**
     * Font size for the debug subtitle overlay (default 24)
     * 
     */
    @JsonProperty("fontSize")
    @JsonPropertyDescription("Font size for the debug subtitle overlay (default 24)")
    private Integer fontSize;

    /**
     * No args constructor for use in serialization
     * 
     */
    public SyncFrameStyle() {
    }

    /**
     * 
     * @param postRemovalGapMs
     *     Gap after removing the overlay before the next action (default 80ms).
     * @param displayDurationMs
     *     How long the green QR overlay is shown per frame (default 160ms = ~4 frames at 25fps).
     * @param debugOverlay
     *     Show narration text as subtitle overlay during recording.
     * @param fontSize
     *     Font size for the debug subtitle overlay (default 24).
     */
    public SyncFrameStyle(Integer displayDurationMs, Integer postRemovalGapMs, Boolean debugOverlay, Integer fontSize) {
        super();
        this.displayDurationMs = displayDurationMs;
        this.postRemovalGapMs = postRemovalGapMs;
        this.debugOverlay = debugOverlay;
        this.fontSize = fontSize;
    }

    /**
     * How long the green QR overlay is shown per frame (default 160ms = ~4 frames at 25fps)
     * 
     */
    @JsonProperty("displayDurationMs")
    public Integer getDisplayDurationMs() {
        return displayDurationMs;
    }

    /**
     * How long the green QR overlay is shown per frame (default 160ms = ~4 frames at 25fps)
     * 
     */
    @JsonProperty("displayDurationMs")
    public void setDisplayDurationMs(Integer displayDurationMs) {
        this.displayDurationMs = displayDurationMs;
    }

    /**
     * Gap after removing the overlay before the next action (default 80ms)
     * 
     */
    @JsonProperty("postRemovalGapMs")
    public Integer getPostRemovalGapMs() {
        return postRemovalGapMs;
    }

    /**
     * Gap after removing the overlay before the next action (default 80ms)
     * 
     */
    @JsonProperty("postRemovalGapMs")
    public void setPostRemovalGapMs(Integer postRemovalGapMs) {
        this.postRemovalGapMs = postRemovalGapMs;
    }

    /**
     * Show narration text as subtitle overlay during recording
     * 
     */
    @JsonProperty("debugOverlay")
    public Boolean getDebugOverlay() {
        return debugOverlay;
    }

    /**
     * Show narration text as subtitle overlay during recording
     * 
     */
    @JsonProperty("debugOverlay")
    public void setDebugOverlay(Boolean debugOverlay) {
        this.debugOverlay = debugOverlay;
    }

    /**
     * Font size for the debug subtitle overlay (default 24)
     * 
     */
    @JsonProperty("fontSize")
    public Integer getFontSize() {
        return fontSize;
    }

    /**
     * Font size for the debug subtitle overlay (default 24)
     * 
     */
    @JsonProperty("fontSize")
    public void setFontSize(Integer fontSize) {
        this.fontSize = fontSize;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(SyncFrameStyle.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("displayDurationMs");
        sb.append('=');
        sb.append(((this.displayDurationMs == null)?"<null>":this.displayDurationMs));
        sb.append(',');
        sb.append("postRemovalGapMs");
        sb.append('=');
        sb.append(((this.postRemovalGapMs == null)?"<null>":this.postRemovalGapMs));
        sb.append(',');
        sb.append("debugOverlay");
        sb.append('=');
        sb.append(((this.debugOverlay == null)?"<null>":this.debugOverlay));
        sb.append(',');
        sb.append("fontSize");
        sb.append('=');
        sb.append(((this.fontSize == null)?"<null>":this.fontSize));
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
        result = ((result* 31)+((this.postRemovalGapMs == null)? 0 :this.postRemovalGapMs.hashCode()));
        result = ((result* 31)+((this.fontSize == null)? 0 :this.fontSize.hashCode()));
        result = ((result* 31)+((this.displayDurationMs == null)? 0 :this.displayDurationMs.hashCode()));
        result = ((result* 31)+((this.debugOverlay == null)? 0 :this.debugOverlay.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof SyncFrameStyle) == false) {
            return false;
        }
        SyncFrameStyle rhs = ((SyncFrameStyle) other);
        return (((((this.postRemovalGapMs == rhs.postRemovalGapMs)||((this.postRemovalGapMs!= null)&&this.postRemovalGapMs.equals(rhs.postRemovalGapMs)))&&((this.fontSize == rhs.fontSize)||((this.fontSize!= null)&&this.fontSize.equals(rhs.fontSize))))&&((this.displayDurationMs == rhs.displayDurationMs)||((this.displayDurationMs!= null)&&this.displayDurationMs.equals(rhs.displayDurationMs))))&&((this.debugOverlay == rhs.debugOverlay)||((this.debugOverlay!= null)&&this.debugOverlay.equals(rhs.debugOverlay))));
    }

}
