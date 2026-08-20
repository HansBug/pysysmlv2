state def VehicleStates {
    first start then off;
    state off;
    // This is a shorthand for a transition whose source is the lexically previous state.
    accept VehicleStartSignal
    then starting;
    state starting;
    accept VehicleOnSignal
    then on;
    state on;
    accept VehicleOffSignal
    then off;
}
