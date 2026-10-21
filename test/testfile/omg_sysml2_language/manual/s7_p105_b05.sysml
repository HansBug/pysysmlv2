part monitor {
action sendReadingTo {
in part destination;
perform getReading {out reading : SensorReading; }
// Send a reading from the monitor to the destination.
action sendReading
send getReading.reading via monitor to destination;
// The following send action is equivalent to the
// one above, but without a name.
send getReading.reading via monitor to destination;
}
}
