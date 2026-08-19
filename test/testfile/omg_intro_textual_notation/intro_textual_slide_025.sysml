part tank : FuelTankAssembly {
    port redefines fuelTankPort {
        // The feature value notation combines the definition of a feature with a binding connection.
        // This is a binding, not an initial or default value.
        out item redefines fuelSupply = pump.pumpOut;
        in item redefines fuelReturn;
    }
    part pump : FuelPump {
        out item pumpOut : Fuel;
        in item pumpIn : Fuel;
    }
    part tank : FuelTank {
        out item fuelOut : Fuel;
        in item fuelIn : Fuel = fuelTankPort.fuelReturn;
    }
}
