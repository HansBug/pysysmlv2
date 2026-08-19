part vehicleTestConfig : Vehicle { ... }
// This is a verification case usage in which the subject has been restricted to a specific test configuration.
verification vehicleMassTest : VehicleMassTest {
    subject testVehicle :> vehicleTestConfig;
}
part massVerificationSystem : MassVerificationSystem {
    perform vehicleMassTest;
    part scale : Scale {
        perform vehicleMassTest.collectData {
            in part :>> testVehicle;
            bind measurement = testVehicle.mass;
            out :>> massMeasured = measurement;
        }
    }
}
