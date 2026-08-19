// Like performed actions, exhibited states are not composite features, therefore, a localClock on a part will not apply to performed actions or exhibited states of the part.
part vehicle : Vehicle {
    part vehicleController : VehicleController;
    // exhibit identifies the part that is exhibiting states that are defined elsewhere.
    exhibit vehicleStates {
        // Parameters for a state usage can be bound in the same way as parameters of an action usage.
        in operatingVehicle = vehicle;
        in controller = vehicleController;
    }
}
