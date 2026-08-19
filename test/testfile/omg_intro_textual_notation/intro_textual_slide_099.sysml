individual def TestSystem :> MassVerificationSystem;
individual def TestVehicle1 :> Vehicle;
individual def TestVehicle2 :> Vehicle;
// Individuals can be used to model the carrying out of actual tests.
individual testSystem : TestSystem :> massVerificationSystem {
    timeslice test1 {
        perform action :>> vehicleMassTest {
            individual :>> testVehicle : TestVehicle1 {
                :>> mass = 2500[SI::kg];
            }
        }
    }
    then timeslice test2 {
        perform action :>> vehicleMassTest {
            individual :>> testVehicle : TestVehicle2 {
                :>> mass = 3000[SI::kg];
            }
        }
    }
}
