part def Vehicle {
    // Actually, any identifiable element can have a short name, not just requirements.
    attribute dryMass: MassValue;
    attribute fuelMass: MassValue;
    attribute fuelFullMass: MassValue;
    ...
}
// A requirement definition may have a modeler specified short name, which is an alternate name for it.
requirement def <'1'> VehicleMassLimitationRequirement :> MassLimitationRequirement {
    doc /* The total mass of a vehicle shall be less than or equal to the required mass. */
    // A requirement definition is always about some subject, which may be implicit or specified explicitly.
    subject vehicle : Vehicle;
    // Features of the subject can be used in the requirement definition.
    attribute redefines massActual = vehicle.dryMass + vehicle.fuelMass;
    // A requirement definition may also specify one or more assumptions.
    assume constraint { vehicle.fuelMass > 0[kg] }
}
