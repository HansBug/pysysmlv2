requirement vehicleMassRequirement {
    subject vehicle : Vehicle;
    // Parameterizing the requirement allows it to be checked against a measured massActual, while asserting (below) that this must be equal to the vehicle.mass.
    in massActual :> ISQ::mass;
    doc  /* The vehicle mass shall be less
    * than or equal to 2500 kg. */
    require constraint {
        massActual == vehicle.mass and
        massActual <= 2500[SI::kg] }
}
// A verification case definition defines a process for verifying whether a subject satisfies one or more requirements.
verification def VehicleMassTest {
    private import VerificationCases::*;
    // The subject may be specified similarly to the subject of a requirement or analysis case.
    subject testVehicle : Vehicle;
    // The requirements to be verified are declared in the verification case objective. The subject of the verification case is automatically bound to the subject of the verified requirements.
    objective vehicleMassVerificationObjective {
        verify vehicleMassRequirement;
    }
    // A verification case always returns a verdict of type VerdictKind. (The default name is verdict, but a different name can be used if desired.)
    // VerdictKind is an enumeration with allowed values pass, fail, inconclusive and error.
    return verdict : VerdictKind;
}
