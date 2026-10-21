part monitor {
action sendReadingTo {
in part destination;
perform getReading {out reading : SensorReading; }
flow getReading.reading to sendReading.payload;
action sendReading send {
in payload;
in sender = monitor;
in receiver = destination;
}
send getReading.reading {
// payload parameter is already bound in the "send" declaration.
in sender = monitor;
in receiver = destination;
}
}
}
