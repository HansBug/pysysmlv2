individual part def Vehicle_1 :> Vehicle {
    snapshot part vehicle_1_t0 : Vehicle_1 {
        :>> mass = 2000.0;
        :>> status {
            :>> gearSetting = 0;
            :>> acceleratorPosition = 0.0;
        }
    }
    // The values of the attributes of an individual can change over time.
    snapshot part vehicle_1_t1 : Vehicle_1 {
        :>> mass = 1500.0;
        :>> status {
            :>> gearSetting = 2;
            :>> acceleratorPosition = 0.5;
        }
    }
    // As usual, succession asserts that the first snapshot occurs before the second in time, in some context.
    first vehicle_1_t0 then vehicle_1_t1;
}
