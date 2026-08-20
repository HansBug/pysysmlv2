abstract part vehicleFamily : Vehicle {
    // A variation definition can be used like any other definition, but valid values of the usage are restricted to the allowed variants of the variation.
    part engine : EngineChoices[1];
    // Any kind of usage can also be a variation, defining allowable variants without a separate variation definition.
    variation part transmission : Transmission[1] {
        variant manualTransmission;
        variant automaticTransmission;
    }
    // A constraint can be used to model restrictions across the choices that can be made.
    assert constraint {
        // The operator xor means "exclusive or". So, this constraint means "choose either a 4cylEngine and a manualTransmission, or a 6cylEngine and an automaticTransmission".
        (engine == engine::'4cylEngine' and
        transmission == transmission::manualTransmission) xor
        (engine == engine::'6cylEngine' and
        transmission == transmission::automaticTransmission)
    }
}
