state def VehicleStates;
// A parallel state is one whose nested states are concurrent.
state vehicleStates : VehicleStates parallel {
    state operationalStates {
        first start then off;
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
    // Transitions are not allowed between concurrent states.
    state healthStates {
        ...
    }
}
