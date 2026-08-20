// A requirement may optionally have its own short name.
// A requirement is the usage of a requirement definition.
requirement <'1.1'> fullVehicleMassLimit : VehicleMassLimitationRequirement {
    subject vehicle : Vehicle;
    // A requirement will often bind requirement definition parameters to specific values.
    attribute :>> massReqd = 2000[kg];
    assume constraint {
        doc /* Fuel tank is full. */
        vehicle.fuelMass == vehicle.fuelFullMass
    }
}
requirement <'1.2'> emptyVehicleMassLimit : VehicleMassLimitationRequirement {
    subject vehicle : Vehicle;
    attribute :>> massReqd = 1500[kg];
    assume constraint {
        doc /* Fuel tank is empty. */
        vehicle.fuelMass == 0[kg]
    }
}
