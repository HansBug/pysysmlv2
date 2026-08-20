// An element from a variability model with variation usages can be configured by specializing it and making selections for each of the variations.
part vehicle4Cyl :> vehicleFamily {
    // A selection is made for a variation by binding one of the allowed variants to the variation usage.
    part redefines engine = engine::'4cylEngine';
    part redefines transmission = transmission::manualTransmission;
}
// Choosing a manualTransmission with a 6cylEngine is not allowed by the constraint asserted on vehicleFamily, so this model of vehicle6Cyl is invalid.
part vehicle6Cyl :> vehicleFamily {
    part redefines engine = engine::'6cylEngine';
    part redefines transmission = transmission::manualTransmission;
}
