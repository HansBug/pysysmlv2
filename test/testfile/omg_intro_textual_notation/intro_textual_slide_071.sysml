individual item def Alice :> Person;
individual item def Bob :> Person;
individual part : Vehicle_1 {
    // A time slice represents an individual over some period of time (that this is a time slice of a part is implicit).
    timeslice aliceDriving {
        // During this time slice of Vehicle_1, Alice has the role of the driver.
        ref individual item :>> driver : Alice;
        // start and done are snapshots at the beginning and end of the time slice.
        snapshot :>> start {
            :>> mass = 2000.0;
        }
        snapshot :>> done {
            :>> mass = 1500.0;
        }
    }
    // Succession asserts that the first time slice must complete before the second can begin.
    then timeslice bobDriving {
        // During a later time slice of Vehicle_1, Bob has the role of the driver.
        ref individual item :>> driver : Bob;
    }
}
