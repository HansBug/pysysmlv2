// A state can be explicitly declared to be a usage of a state definition.
state def VehicleStates;
state vehicleStates : VehicleStates {
    first start then off;
    // A state can also be directly decomposed into other states.
    state off;
    accept VehicleStartSignal
    then starting;
    state starting;
    accept VehicleOnSignal
    then on;
    state on;
    accept VehicleOffSignal
    then off;
}
