// The related elements of this connection definition
// are the part definitions Hub and Device.
connection def DeviceConnection {
  end part hub : Hub;
  end part device : Device;

  // This is a non-end feature of the connection definition.
  attribute bandwidth : Real;
}
