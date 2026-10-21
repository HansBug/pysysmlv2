package VerificationCaseDefinitions {
    verification def MassTest;
    verification def AccelerationTest;
    verification def ReliabilityTest;
}
package VerificationCases1 {
    verification massTests : MassTest {
        subject = vehicle_b;
        objective {
            verify vehicleSpecification.vehicleMassRequirement {
                redefines massActual = weighVehicle.massMeasured;
            }
        }
        metadata VerificationMethod {
            kind = VerificationMethodKind::test;
        }
        action weighVehicle {
            out massMeasured :> ISQ::mass;
        }
        then action evaluatePassFail {
            in massMeasured :> ISQ::mass;
            out verdict = PassIf(
                vehicleSpecification.vehicleMassRequirement(vehicle_b)
            );
        }
        flow from weighVehicle.massMeasured to evaluatePassFail.massMeasured;
        return :>> verdict = evaluatePassFail.verdict;
    }
}
package VerificationSystem {
    part massVerificationSystem {
        perform massTests;
        part scale {
            perform massTests.weighVehicle;
        }
        part operator {
            perform massTests.evaluatePassFail;
        }
    }
}
