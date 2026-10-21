part def FuelTank {
    attribute mass :> ISQ::mass;
    attribute fuelKind : FuelKind;
    ref item fuel : Fuel {
        attribute redefines fuelMass;
    }
    attribute fuelMassMax :> ISQ::mass;
    assert constraint fuelConstraint { fuel.fuelMass <= fuelMassMax }
    port fuelOutPort : FuelPort;
    port fuelInPort : ~FuelPort;
}
