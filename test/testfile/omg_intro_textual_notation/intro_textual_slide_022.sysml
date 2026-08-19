// An interface definition is a connection definition whose ends are ports.
interface def FuelInterface {
    // The default cross multiplicity is 0..*.
    end port supplierPort : FuelOutPort;
    end port consumerPort : FuelInPort;
}
part vehicle : Vehicle {
    part tankAssy : FuelTankAssembly;
    part eng : Engine;
    // An interface usage is a connection usage defined by an interface definition, connecting two compatible ports.
    interface : FuelInterface connect
    supplierPort ::> tankAssy.fuelTankPort to
    consumerPort ::> eng.engineFuelPort;
}
