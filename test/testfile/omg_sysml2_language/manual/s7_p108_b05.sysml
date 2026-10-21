part controller {
perform action accepting {
// The receiver for the following accept action is, by default,
// the accepting context, which is the "accepting" action,
// not the part "controller".
accept reading : SensorReading;
// ...
}
}
