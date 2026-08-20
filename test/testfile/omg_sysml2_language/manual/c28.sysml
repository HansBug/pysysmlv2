part def Vehicle {
  part fuelTank {
    out fuelFlowOut : Fuel;
  }
  part engine {
    in fuelFlowIn : Fuel;
  }
  binding fuelFlowBinding
    bind fuelTank.fuelFlowOut = engine.fuelFlowIn;

  // The following is equivalent to the above, but
  // without the name.
  bind fuelTank.fuelFlowOut = engine.fuelFlowIn;
}
