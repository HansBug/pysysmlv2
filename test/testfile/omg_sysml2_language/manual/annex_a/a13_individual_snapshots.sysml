individual a : VehicleRoadContext_1 {
    timeslice t0_t2_a {
        snapshot t0_a {
            attribute t0 redefines time = 0[s];
            snapshot t0_r : Road_1 {
                :>>incline = 0;
                :>>friction = .1;
            }
            snapshot t0_v : Vehicle_1 {
                :>>position = 0[m];
                :>>velocity = 0[m/s];
                :>>acceleration = 1.96[m/s**2];
                snapshot t0_fa : FrontAxleAssembly_1 {
                    snapshot t0_leftFront : Wheel_1;
                    snapshot t0_rightFront : Wheel_2;
                }
            }
        }
        snapshot t1_a {
            attribute t1 redefines time = 1[s];
            snapshot t1_r : Road_1 {
                :>>incline = 0;
                :>>friction = .1;
            }
            snapshot t1_v : Vehicle_1 {
                :>>position = .98[m];
                :>>velocity = 1.96[m/s];
                :>>acceleration = 1.96[m/s**2];
                snapshot t1_fa : FrontAxleAssembly_1 {
                    snapshot t1_leftFront : Wheel_1;
                    snapshot t1_rightFront : Wheel_2;
                }
            }
        }
        snapshot t2_a {
            attribute t2 redefines time = 2[s];
            snapshot t2_r : Road_1 {
                :>>incline = 0;
                :>>friction = .1;
            }
            snapshot t2_v : Vehicle_1 {
                :>>position = 3.92[m];
                :>>velocity = 3.92[m/s];
                :>>acceleration = 1.96[m/s**2];
                snapshot t2_fa : FrontAxleAssembly_1 {
                    snapshot t2_leftFront : Wheel_1;
                    snapshot t2_rightFront : Wheel_2;
                }
            }
        }
    }
}
