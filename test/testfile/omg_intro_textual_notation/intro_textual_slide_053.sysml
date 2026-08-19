action performSelfTest{in vehicle : Vehicle;}
state def VehicleStates {
    in operatingVehicle : Vehicle;
    in controller : VehicleController; }
state vehicleStates : VehicleStates {
    in operatingVehicle : Vehicle;
    in controller : VehicleController;
    first start then off;
    state off;
    accept VehicleStartSignal
    // A guard is a condition that must be true for a transition to fire.
    if operatingVehicle.brakePedalDepressed
    // An effect action is performed when a transition fires, before entry to the target state.
    do send new ControllerStartSignal() to controller
    then starting;
    state starting;
    accept VehicleOnSignal
    then on;
    state on { ... }
    accept VehicleOffSignal
    then off;
}
