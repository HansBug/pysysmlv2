part def Vehicle {
  part fuelTank : FuelTank {
    out fuelOut : Fuel;
  }
  part engine : Engine {
    in fuelIn : Fuel;
  }
  // This flow usage actually connects the fuelTank to the
  // engine. The transfer moves Fuel from fuelOut to fuelIn.
  flow fuelFlow : FuelFlow of flowingFuel : Fuel
    from fuelTank.fuelOut to engine.fuelIn;
  // The following is equivalent to the above,
  // and leaving the flow definition and payload implicit.
  flow fuelTank.fuelOut to engine.fuelIn;
}
