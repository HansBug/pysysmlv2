// A port definition defines features that can be made available via ports. (Replaces interface blocks in SysML v1).
port def FuelOutPort {
    attribute temperature : Temp;
    // Ports may have attribute and reference features. A feature with a direction (in, out or inout) is a directed feature.
    // Directed features are always referential, so it is not necessary to explicitly use the ref keyword.
    out item fuelSupply : Fuel;
    in item fuelReturn : Fuel;
}
port def FuelInPort {
    attribute temperature : Temp;
    // Two ports are compatible for connection if they have directed features that match with inverse directions.
    in item fuelSupply : Fuel;
    out item fuelReturn : Fuel;
}
part def FuelTankAssembly {
    // A port is a connection point through which a part definition makes some of its features available in a limited way. (Like a proxy port in SysML v1.)
    port fuelTankPort : FuelOutPort;
}
part def Engine {
    port engineFuelPort : FuelInPort;
}
