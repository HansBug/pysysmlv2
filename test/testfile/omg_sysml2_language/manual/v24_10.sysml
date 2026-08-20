verification def VehicleMassTest {
    import VerificationCases::*;

    subject testVehicle : Vehicle;
    objective vehicleMassVerificationObjective {
        // The subject of the verify is automatically bound to "testVehicle".
        verify vehicleMassRequirement;
    }

    metadata VerificationMethod {
        kind = VerificationMthodKind::test;
    }

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
            // Check that "testVehicle" statisfies "vehicleMassRequirement"
            // if its mass equals 'massProcessed'.
            PassIf(vehicleMassRequirement(
                vehicle = testVehicle,
                massActual = massProcessed)
            );
    }

    return verdict : VerdictKind = evaluateData.verdict;
}
