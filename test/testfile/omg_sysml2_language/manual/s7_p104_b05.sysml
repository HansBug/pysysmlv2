part def Vehicle {
perform action powerVehicle references VehicleActions::providePower;
abstract perform action moveVehicle; // Performed action is itself.
}
