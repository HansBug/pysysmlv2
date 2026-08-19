// Definitions
part def Vehicle;
part def Engine;
part def Cylinder;
// Usages
// Composite structure can be specified entirely on parts.
part vehicle : Vehicle {
    part eng : Engine {
        part cyl : Cylinder[4..6];
    }
}
// A part can specialize another part.
part smallVehicle :> vehicle {
    part redefines eng {
        part redefines cyl[4];
    }
}
part bigVehicle :> vehicle {
    part redefines eng {
        part redefines cyl[6];
    }
}
