requirement def VehicleRequirementsGroup {
    subject vehicle : Vehicle;

    // The subject of the following subrequirements
    // are implicitly bound to the subject "vehicle"
    // of the containing requirement definition.
    requirement driving : DrivingRequirement;
    requirement braking : BrakingRequirement;

    // The subject of the following subrequirement
    // is declared explicitly.
    requirement engineRqts : EngineRequirementsGroup {
        subject engine = vehicle.engine;
    }
}
