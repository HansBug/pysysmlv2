standard library package ShapeItems {
    ...
    item def Disc :> Shell, PlanarSurface {
        attribute :>> semiMajorAxis;
        attribute :>> semiMinorAxis;
        item :>> shape : Ellipse [1] {
            attribute :>> semiMajorAxis = Disc::semiMajorAxis;
            attribute :>> semiMinorAxis = Disc::semiMinorAxis;
        }
        ...
    }
    item def CircularDisc :> Disc {
        attribute :>> radius [1];
        attribute :>> semiMajorAxis [1] = radius;
        attribute :>> semiMinorAxis [1] = radius;
        item :>> shape : Circle { ... }
        ...
    }
    item def ConicSurface :> Shell {
        ...
    }
    ...
}
