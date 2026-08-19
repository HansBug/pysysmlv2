// A state definition is like a state machine in UML and SysML v1. It defines a behavioral state that can be exhibited by a system.
state def VehicleStates {
    // This indicates the initial state after entry is "off".
    first start then off;
    // A state definition can specify a set of discrete nested states.
    state off;
    transition off_to_starting
    first off
    // States are connected by transitions that fire on acceptance of item transfers (like accept actions).
    accept VehicleStartSignal
    then starting;
    state starting;
    transition starting_to_on
    first starting
    accept VehicleOnSignal
    then on;
    state on;
    transition on_to_off
    first on
    accept VehicleOffSignal
    then off;
}
