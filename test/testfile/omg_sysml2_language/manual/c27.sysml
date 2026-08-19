connection connection1 : DeviceConnection {
  end [1] part hub ::> mainSwitch; // Implicitly redefines DeviceConnection::hub.
  end [1] part device ::> sensorFeed; // Implicitly redefines DeviceConnection::device.
}
