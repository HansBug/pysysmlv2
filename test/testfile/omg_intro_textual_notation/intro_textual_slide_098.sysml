part vehicleTestConfig : Vehicle { ... }
// This is a verification case usage in which the subject has been restricted to a specific test configuration.
verification vehicleMassTest : VehicleMassTest {
    subject testVehicle :> vehicleTestConfig;
}
part massVerificationSystem : MassVerificationSystem {
    // A verification case can be performed as an action by a verification system.
    perform vehicleMassTest;
    part scale : Scale {
        // Parts of the verification system can perform steps in the overall verification process.
        perform vehicleMassTest.collectData {
            in part :>> testVehicle;
            // In reality, this would be some more involved process to determine the measured mass.
            bind measurement = testVehicle.mass;
            out :>> massMeasured = measurement;
        }
    }
}
