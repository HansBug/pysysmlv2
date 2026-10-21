part monitor {
action sendReadingTo {
in part destination;
perform getReading {out reading : SensorReading; }
// The sender for the following send action is, by default,
// the sending context, which is the part "monitor".
send getReading.reading to destination;
}
}
