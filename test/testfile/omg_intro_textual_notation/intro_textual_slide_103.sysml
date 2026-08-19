abstract part vehicleFamily : Vehicle {
    part engine : EngineChoices[1];
    // Any kind of usage can also be a variation, defining allowable variants without a separate variation definition.
    variation part transmission : Transmission[1] {
        variant manualTransmission;
        variant automaticTransmission;
    }
    assert constraint {
        (engine == engine::'4cylEngine' and
        transmission == transmission::manualTransmission) xor
        (engine == engine::'6cylEngine' and
        transmission == transmission::automaticTransmission)
    }
}
