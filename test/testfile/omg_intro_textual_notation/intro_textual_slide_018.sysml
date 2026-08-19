// A connection definition is a part definition whose usages are connections between its ends.
connection def PressureSeat {
    end [1] part bead : TireBead;
    end [1] part mountingRim: TireMountingRim;
}
part wheelHubAssembly : WheelHubAssembly {
    part wheel : WheelAssembly[1] {
        part t : Tire[1] {
            part bead : TireBead[2];
        }
        part w: Wheel[1] {
            part rim : TireMountingRim[2];
            part mountingHoles : LugBoltMountingHole[5];
        }
        // A connection is a usage of a connection definition, which connects two other features.
        connection : PressureSeat
        // Reference subsetting (references or :>) relates feature to a connector ends. “Dot” notation specifies paths to nested features.
        connect bead references t.bead
            to mountingRim references w.rim;
    }
    part lugBoltJoints : LugBoltJoint[0..5];
    part hub : Hub[1] {
        part h : LugBoltThreadableHole[5];
    }
    // Cross multiplicities constrain the number of connections, rather than end values. E.g., for every TireBead there must be a PressureSeat connection to exactly one TireMountingRim.
    // If a connection definition is not specified, a generic connection definition (called Connection) is used.
    connect [0..1] lugBoltJoints to [1] wheel.w.mountingHoles;
    connect [0..1] lugBoltJoints to [1] hub.h;
}
