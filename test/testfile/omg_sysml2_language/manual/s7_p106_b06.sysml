part def MonitorDevice {
port readingPort;
action monitoring {
perform getReading {out reading : SensorReading; }
send getReading.reading via readingPort;
}
}
