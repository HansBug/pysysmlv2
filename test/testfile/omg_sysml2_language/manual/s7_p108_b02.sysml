part controller {
in level : Real;
attribute threshold : Real;
action {
// Both of the following accept actions trigger (once) when the
// given expression becomes true.
accept : ChangeSignal = Triggers::triggerWhen({ level > threshold });
accept when level > threshold;
// The following accept action triggers at the given date and time.
accept at Iso8601DateTime("2024-02-01T00:00:00Z");
// The following accept action triggers 30 seconds after the evaluation
// of its time trigger.
accept after 30 [s];
}
}
