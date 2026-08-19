standard library package ShapeItems {
    ...
    item def Ellipsoid :> ConicSurface {
        attribute semiAxis1 : LengthValue [1] :> scalarQuantities;
        attribute semiAxis2 : LengthValue [1] :> scalarQuantities;
        attribute semiAxis3 : LengthValue [1] :> scalarQuantities;
        ...
    }
    item def Sphere :> Ellipsoid {
        attribute :>> radius [1];
        attribute :>> semiAxis1 [1] = radius;
        attribute :>> semiAxis2 [1] = radius;
        attribute :>> semiAxis3 [1] = radius;
    }
    item def Paraboloid :> ConicSurface {
        attribute focalDistance : LengthValue [1] :> scalarQuantities;
        ...
    }
    ...
}
