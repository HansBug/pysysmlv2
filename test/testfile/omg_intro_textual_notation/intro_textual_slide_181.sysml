// The ShapeItems package provides a model of items that represent basic geometric shapes.
standard library package ShapeItems {
    ...
    item def PlanarCurve :> Curve {
        attribute :>> length [1];
        ...
    }
    item def Line :> PlanarCurve {
        attribute :>> length;
        attribute :>> outerSpaceDimension = 1;
    }
    item def PlanarSurface :> Surface {
        attribute :>> area;
        attribute :>> outerSpaceDimension = 2;
        item :>> shape : PlanarCurve;
    }
    abstract item def Path :> StructuredCurve;
    abstract item def Shell :> StructuredSurface;
    ...
}
