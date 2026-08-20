// Every port definition has an implicit conjugate port definition that reverses input and output features. It has the name of the original definition with ~ prepended (e.g., ~FuelPort).
port def FuelPort {
    attribute temperature : Temp;
    out item fuelSupply : Fuel;
    in item fuelReturn : Fuel;
}
part def FuelTankAssembly {
    port fuelTankPort : FuelPort;
}
part def Engine {
    // Using a ~ symbol on the port type is a shorthand for using the conjugate port definition (e.g., FuelPort::~FuelPort).
    port engineFuelPort : ~FuelPort;
}
