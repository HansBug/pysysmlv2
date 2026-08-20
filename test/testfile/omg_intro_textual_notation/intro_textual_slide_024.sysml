part tank : FuelTankAssembly {
    port redefines fuelTankPort {
        out item redefines fuelSupply;
        in item redefines fuelReturn;
    }
    // A binding connection is a connection that asserts the equivalence of the connected features (i.e., they have equal values in the same context).
    bind fuelTankPort.fuelSupply = pump.pumpOut;
    bind fuelTankPort.fuelReturn = tank.fuelIn;
    part pump : FuelPump {
        // Usages on parts can also have direction (and are automatically referential).
        out item pumpOut : Fuel;
        in item pumpIn : Fuel;
    }
    part tank : FuelTank {
        out item fuelOut : Fuel;
        in item fuelIn : Fuel;
    }
}
