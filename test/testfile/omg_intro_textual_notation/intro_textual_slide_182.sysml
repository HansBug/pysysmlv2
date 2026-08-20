standard library package ShapeItems {
    ...
    item def ConicSection :> Path, PlanarCurve {
        ...
    }
    item def Ellipse :> ConicSection {
        attribute :>> semiMajorAxis;
        attribute :>> semiMinorAxis;
        ...
    }
    item def Circle :> Ellipse {
        attribute :>> radius;
        attribute :>> semiMajorAxis = radius;
        attribute :>> semiMinorAxis = radius;
        ...
    }
    ...
    item def Polygon :> Path, PlanarCurve {
        item :>> edges : Line { item :>> vertices [2]; }
        attribute :>> isClosed = true;
        ...
    }
    ...
}
