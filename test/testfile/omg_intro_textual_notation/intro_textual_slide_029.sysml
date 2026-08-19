// A flow definition is used to assert that a flow must exist between the instances of part definitions.
flow def FuelFlow {
    // The definition can (optionally) constrain the payload transferred by usages.
    ref :>> payload : Fuel;
    // Note that the default end multiplicities on this connection are 1 to 1.
    end port fuelOut : FuelOutPort;
    end port fuelIn : FuelInPort;
}
part vehicle : Vehicle {
    part tankAssy : FuelTankAssembly;
    part eng : Engine;
    // This usage realizes the required flow between the tankAssy.fuelTankPort and the eng.engineFuelPort.
    // The payload should be consistent with what is declared in the flow definition (if any).
    flow : FuelFlow of Fuel
        // The connection is defined to be between the ports, but the transfer is still from an output to an input.
        from tankAssy.fuelTankPort.fuelSupply
        to eng.engineFuelPort.fuelSupply;
}
