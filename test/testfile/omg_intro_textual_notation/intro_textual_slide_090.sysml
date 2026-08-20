// A requirement may also be used to group other requirements.
requirement vehicleSpecification {
    doc /* Overall vehicle requirements group */
    subject vehicle : Vehicle;
    // Grouped requirements are treated as required constraints of the group.
    // Requirements can be grouped by reference...
    require fullVehicleMassLimit;
    require emptyVehicleMassLimit;
}
part def Engine {
    port clutchPort: ClutchPort;
    perform action generateTorque: GenerateTorque;
}
requirement engineSpecification {
    doc /* Engine power requirements group */
    // By default, the subject of grouped requirements is assumed to be the same as that of the group.
    subject engine : Engine;
    // ...or by composition.
    requirement drivePowerInterface : DrivePowerInterfaceRequirement {
        // The subject of a grouped requirement can also be bound explicitly.
        subject clutchPort = engine.clutchPort;
    }
    requirement torqueGeneration : TorqueGenerationRequirement {
        subject generateTorque = engine.generateTorque;
    }
}
