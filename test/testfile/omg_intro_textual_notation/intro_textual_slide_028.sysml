interface def FuelInterface {
    end supplierPort : FuelOutPort;
    end consumerPort : FuelInPort;
    // Flows can be defined within an interface definition.
    flow supplierPort.fuelSupply to consumerPort.fuelSupply;
    flow consumerPort.fuelReturn to supplierPort.fuelReturn;
}
part vehicle : Vehicle {
    part tankAssy : FuelTankAssembly;
    part eng : Engine;
    // The flows are established when the interface is used.
    interface : FuelInterface connect
    supplierPort ::> tankAssy.fuelTankPort to
    consumerPort ::> eng.engineFuelPort;
}
