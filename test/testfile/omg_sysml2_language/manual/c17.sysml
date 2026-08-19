part def Hub {
  ref part connectedDevices [1..*] ordered : Device;
}
part def Device {
  ref part connectingHub [0..1] : Hub;
}
connection def DeviceConnection {
  end part hub : Hub crosses device.connectingHub;
  end part device : Device => hub.connectedDevices;
  attribute bandwidth : Real;
}
