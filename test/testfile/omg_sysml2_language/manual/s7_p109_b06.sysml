action def UpdateVehiclePosition {
in part sim : Simulation;
in attribute deltaT : TimeDurationValue;
// The target of the assignment below is "sim".
// The referent feature chain is "vehicle.position".
assign sim.vehicle.position :=
sim.vehicle.position + sim.vehicle.velocity * deltaT;
// After the above assignment "sim.vehicle.position" has the
// value of the result of the assigned value expression,
// evaluated at the time of the assignment.
}
action def RecordNames {
in item record : Record;
in item entries : Entry[1..*];
// "entries.name" evaluates to the names of all entries.
// These values are assigned to the "names" feature of "record".
assign record.names := entries.name;
}
