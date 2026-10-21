part monitor {
ref part destination;
perform action sending {
perform getReading {out reading : SensorReading; }
// The sender for the following send action is, by default,
// the sending context, which is the action "sending",
// not the part "monitor".
send getReading.reading to destination;
}
}
