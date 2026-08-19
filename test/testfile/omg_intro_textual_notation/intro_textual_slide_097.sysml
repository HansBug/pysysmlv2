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
        PassIf(vehicleMassRequirement(
        vehicle = testVehicle,
        massActual = massProcessed));
    }
    return verdict : VerdictKind = evaluateData.verdict;
}
