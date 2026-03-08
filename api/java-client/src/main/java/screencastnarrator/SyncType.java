package screencastnarrator;

public enum SyncType {
    INIT("init"),
    NARRATION("nar"),
    ACTION("act"),
    HIGHLIGHT("hlt"),
    DONE("done");

    private final String value;

    SyncType(String value) {
        this.value = value;
    }

    public String value() {
        return value;
    }

    @Override
    public String toString() {
        return value;
    }
}
