// An individual usage represents an individual during some portion of its lifetime.
individual part def Vehicle_1 :> Vehicle {
    part leftFrontWheel : Wheel;
    part rightFrontWheel : Wheel;
}
individual part def Wheel_1 :> Wheel;
individual part vehicle_1 : Vehicle_1 {
    snapshot part vehicle_1_t0 {
        // During the first snapshot of vehicle_1, Wheel_1 has the role of the leftFrontWheel.
        snapshot leftFrontWheel_t0 : Wheel_1 :>> leftFrontWheel;
    }
    then snapshot part vehicle_1_t1 {
        // During a later snapshot, the same Wheel_1 has the role of the rightFrontWheel.
        snapshot rightFrontWheel_t1 : Wheel_1 :>> rightFrontWheel;
    }
}
