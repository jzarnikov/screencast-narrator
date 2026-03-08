
package screencastnarrator.generated;

import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "highlightStyle",
    "syncFrameStyle"
})
@Generated("jsonschema2pojo")
public class Options {

    /**
     * User-customizable highlight appearance. All fields are optional — unset fields inherit from the shared config defaults.
     * 
     */
    @JsonProperty("highlightStyle")
    @JsonPropertyDescription("User-customizable highlight appearance. All fields are optional \u2014 unset fields inherit from the shared config defaults.")
    private HighlightStyle highlightStyle;
    /**
     * User-customizable sync frame timing and overlay settings. All fields are optional — unset fields inherit from the shared config defaults.
     * 
     */
    @JsonProperty("syncFrameStyle")
    @JsonPropertyDescription("User-customizable sync frame timing and overlay settings. All fields are optional \u2014 unset fields inherit from the shared config defaults.")
    private SyncFrameStyle syncFrameStyle;

    /**
     * No args constructor for use in serialization
     * 
     */
    public Options() {
    }

    public Options(HighlightStyle highlightStyle, SyncFrameStyle syncFrameStyle) {
        super();
        this.highlightStyle = highlightStyle;
        this.syncFrameStyle = syncFrameStyle;
    }

    /**
     * User-customizable highlight appearance. All fields are optional — unset fields inherit from the shared config defaults.
     * 
     */
    @JsonProperty("highlightStyle")
    public HighlightStyle getHighlightStyle() {
        return highlightStyle;
    }

    /**
     * User-customizable highlight appearance. All fields are optional — unset fields inherit from the shared config defaults.
     * 
     */
    @JsonProperty("highlightStyle")
    public void setHighlightStyle(HighlightStyle highlightStyle) {
        this.highlightStyle = highlightStyle;
    }

    /**
     * User-customizable sync frame timing and overlay settings. All fields are optional — unset fields inherit from the shared config defaults.
     * 
     */
    @JsonProperty("syncFrameStyle")
    public SyncFrameStyle getSyncFrameStyle() {
        return syncFrameStyle;
    }

    /**
     * User-customizable sync frame timing and overlay settings. All fields are optional — unset fields inherit from the shared config defaults.
     * 
     */
    @JsonProperty("syncFrameStyle")
    public void setSyncFrameStyle(SyncFrameStyle syncFrameStyle) {
        this.syncFrameStyle = syncFrameStyle;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(Options.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("highlightStyle");
        sb.append('=');
        sb.append(((this.highlightStyle == null)?"<null>":this.highlightStyle));
        sb.append(',');
        sb.append("syncFrameStyle");
        sb.append('=');
        sb.append(((this.syncFrameStyle == null)?"<null>":this.syncFrameStyle));
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
        result = ((result* 31)+((this.syncFrameStyle == null)? 0 :this.syncFrameStyle.hashCode()));
        result = ((result* 31)+((this.highlightStyle == null)? 0 :this.highlightStyle.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof Options) == false) {
            return false;
        }
        Options rhs = ((Options) other);
        return (((this.syncFrameStyle == rhs.syncFrameStyle)||((this.syncFrameStyle!= null)&&this.syncFrameStyle.equals(rhs.syncFrameStyle)))&&((this.highlightStyle == rhs.highlightStyle)||((this.highlightStyle!= null)&&this.highlightStyle.equals(rhs.highlightStyle))));
    }

}
