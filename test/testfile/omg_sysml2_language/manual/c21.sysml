part def NetworkConfiguration {
  part networkHubs[*] : Axle;
  part networkDevices[*] : Device;
  // Connects each one of the networkHubs to at most four of the networkDevices.
  connection networkConnections : DeviceConnection {
    end [1] part hub references networkHubs;
    end [0..4] part device references networkDevices;
  }
}
