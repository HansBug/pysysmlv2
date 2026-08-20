individual def TestSystem :> MassVerificationSystem;
individual def TestVehicle1 :> Vehicle;
individual def TestVehicle2 :> Vehicle;
// Individuals can be used to model the carrying out of actual tests.
individual testSystem : TestSystem :> massVerificationSystem {
    timeslice test1 {
        // The keyword action is required here to permit the local redefinition.
        perform action :>> vehicleMassTest {
            // The test on the individual TestVehicle1 should pass.
            individual :>> testVehicle : TestVehicle1 {
                :>> mass = 2500[SI::kg];
            }
        }
    }
    then timeslice test2 {
        perform action :>> vehicleMassTest {
            // The test on the individual TestVehicle2 should fail.
            individual :>> testVehicle : TestVehicle2 {
                :>> mass = 3000[SI::kg];
            }
        }
    }
}
