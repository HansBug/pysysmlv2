part vehicle : Vehicle {
    part tankAssy : FuelTankAssembly;
    part eng : Engine;
    // A flow usage is a transfer of some payload from an output of a source port to an input of a target port.
    // Specifying the payload type (e.g., “of Fuel”) is optional.
    flow of Fuel
        from tankAssy.fuelTankPort.fuelSupply
        to eng.engineFuelPort.fuelSupply;
    flow of Fuel
        from eng.engineFuelPort.fuelReturn
        to tankAssy.fuelTankPort.fuelReturn;
}
