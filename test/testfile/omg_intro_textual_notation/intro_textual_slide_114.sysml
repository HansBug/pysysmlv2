private import FailureModelingMetadata::*;
// A user-defined keyword, starting with # and referencing a semantic metadata definition, can be used to declare a definition or usage.
#scenario def DeviceFailure {
    ref device : Device;
    attribute minPower : Real;
    #cause 'battery old' {
        :>> probability = 0.01;
    }
    #causation connect 'battery old' to 'power low';
    #situation 'power low' {
        constraint { device.battery.power < minPower }
    }
    #causation connect 'power low' to 'device shutoff';
    #failure 'device shutoff' {
        :>> severity = LevelEnum::high;
    }
}
