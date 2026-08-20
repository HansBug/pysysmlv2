part vehicle_c1 : Vehicle {
    part engine_v1: Engine { ... }
    ...
}
part 'Vehicle c1 Design Context' {
    ref vehicle_design :> vehicle_c1;
    // A requirement satisfaction asserts that a given requirement is satisfied when its subject parameter is bound to a specific thing.
    // Formally, a requirement is satisfied for a subject if, when all its assumed constraints are true, then all its required constraints are true.
    satisfy vehicleSpecification by vehicle_design;
    satisfy engineSpecification by vehicle_design.engine_v1;
}
