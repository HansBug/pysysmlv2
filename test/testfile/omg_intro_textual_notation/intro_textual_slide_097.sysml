verification def VehicleMassTest {
    private import VerificationCases::*;
    subject testVehicle : Vehicle;
    objective vehicleMassVerificationObjective {
        verify vehicleMassRequirement;
    }
    // The steps of a verification case are actions that, together, determine the verdict.
    action collectData {
        in part testVehicle : Vehicle = VehicleMassTest::testVehicle;
        out massMeasured :> ISQ::mass;
    }
    action processData {
        in massMeasured :> ISQ::mass = collectData.massMeasured;
        out massProcessed :> ISQ::mass;
    }
    action evaluateData {
        in massProcessed :> ISQ::mass = processData.massProcessed;
        out verdict : VerdictKind =
        // PassIf is a utility function that returns a pass or fail verdict depending on whether its argument is true or false.
        // This is a check of whether the requirement is satisfied for the given parameter values.
        PassIf(vehicleMassRequirement(
        // The use of named argument notation here is optional.
        vehicle = testVehicle,
        massActual = massProcessed));
    }
    return verdict : VerdictKind = evaluateData.verdict;
}
