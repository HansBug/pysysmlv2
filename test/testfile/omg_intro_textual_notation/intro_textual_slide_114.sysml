private import FailureModelingMetadata::*;
// A user-defined keyword, starting with # and referencing a semantic metadata definition, can be used to declare a definition or usage.
// Implicitly specializes the library definition Scenario (the definition of the scenarios base type).
#scenario def DeviceFailure {
    ref device : Device;
    attribute minPower : Real;
    #cause 'battery old' {
        :>> probability = 0.01;
    }
    #causation connect 'battery old' to 'power low';
    // Implicitly specializes the library usage situations (as given in the semantic metadata situation).
    #situation 'power low' {
        constraint { device.battery.power < minPower }
    }
    #causation connect 'power low' to 'device shutoff';
    // Inheritance and redefinition work as for explicit specialization.
    #failure 'device shutoff' {
        :>> severity = LevelEnum::high;
    }
}
