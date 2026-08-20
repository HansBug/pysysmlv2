action performSelfTest{in vehicle : Vehicle;}
// States, like actions, can have parameters.
state def VehicleStates{in operatingVehicle : Vehicle;}
state vehicleStates : VehicleStates {
    in operatingVehicle : Vehicle;
    first start then off;
    state off;
    accept VehicleStartSignal
    then starting;
    state starting;
    accept VehicleOnSignal
    then on;
    state on {
        // An entry action is performed on entry to a state, a do action while in it, and an exit action on exit from it.
        entry performSelfTest
        { in vehicle = operatingVehicle; }
        // A state entry, do or exit can reference an action defined elsewhere...
        do action providePower { ... }
        // ... or the action can be defined within the state.
        exit action applyParkingBrake { ... }
    }
    accept VehicleOffSignal
    then off;
}
