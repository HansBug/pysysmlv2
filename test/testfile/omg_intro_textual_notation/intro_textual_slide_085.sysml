// TimeOf and DurationOf are from the Time package in the Quantities and Units Domain Library.
state healthStates {
    in vehicle : Vehicle;
    entry; then normal;
    state normal;
    accept at vehicle.maintenanceTime
    then maintenance;
    state maintenance {
        // TimeOf returns the time of the start of an occurrence (in this example, a state performance).
        assert constraint { TimeOf(maintenance) > vehicle.maintenanceTime }
        assert constraint { TimeOf(maintenance) - TimeOf(normal.done) < 2 [s]
        }
        entry assign vehicle.maintenanceTime :=
        vehicle.maintenanceTime + vehicle.maintenanceInterval;
    }
    accept MaintenanceDone
    then normal;
    // DurationOf returns the time duration of an occurrence (the difference between its start and done times).
    constraint { DurationOf(maintenance) <= 48 [h] }
}
