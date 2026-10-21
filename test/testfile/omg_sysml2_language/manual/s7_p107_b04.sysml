part controller {
action accepting {
// ...
action acceptReading
accept reading : SensorReading via controller;
// The following accept action is equivalent to the
// one above, but it does not name the accept action or
// the payload parameter.
accept SensorReading via controller;
// ...
}
}
