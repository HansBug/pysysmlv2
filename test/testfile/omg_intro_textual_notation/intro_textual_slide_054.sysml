action senseTemperature { out temp : TemperatureValue; }
state healthStates {
    in vehicle : Vehicle;
    in controller : VehicleController;
    do senseTemperature;
    first start then normal;
    state normal;
    // An absolute time trigger fires at a given instant of time.
    // Time instant quantities are defined in the Time package, not the ISQ package.
    accept at vehicle.maintenanceTime
    then maintenance;
    // A change trigger fires when a given Boolean expression becomes true.
    accept when senseTemperature.temp > vehicle.maxTemperature
    do send new OverTemp() to controller
    then degraded;
    state maintenance {
        entry assign vehicle.maintenanceTime :=
        vehicle.maintenanceTime + vehicle.maintenanceInterval;
    }
    // A relative time trigger fires after a given time duration.
    accept after 48 [h]
    then normal;
    state degraded;
    // Change and time triggers can also be used in accept actions.
    accept when senseTemperature.temp <= vehicle.maxTemperature
    then normal;
}
