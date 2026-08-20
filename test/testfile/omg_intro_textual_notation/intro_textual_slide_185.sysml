standard library package ShapeItems {
    ...
    item def ConeOrCylinder :> Shell {
        attribute :>> semiMajorAxis [1];
        attribute :>> semiMinorAxis [1];
        attribute :>> height [1];
        ...
    }
    item def Cone :> ConeOrCylinder { ... }
    item def Cylinder :> ConeOrCylinder { ... }
    ...
    item def Polyhedron :>> Shell { ... }
    item def CuboidOrTriangularPrism :> Polyhedron { ... }
    item def Cuboid :> CuboidOrTriangularPrism { ... }
    item def RectangularCuboid :> Cuboid {
        attribute :>> length [1];
        attribute :>> width [1];
        attribute :>> height [1];
        ...
    }
    alias Box for RectangularCuboid;
    ...
}
