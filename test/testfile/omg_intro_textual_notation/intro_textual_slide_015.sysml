// Definitions
part def Vehicle {
    part eng : Engine;
}
part def Engine {
    part cyl : Cylinder[4..6];
}
part def Cylinder;
// Usages
// Parts can be specified outside the context of a specific part definition.
// The defined by relationship is a kind of generalization.
part smallVehicle : Vehicle {
    // Parts inherit properties from their definitions and can redefine them, to any level of nesting.
    part redefines eng {
        part redefines cyl[4];
    }
}
part bigVehicle : Vehicle {
    part redefines eng {
        part redefines cyl[6];
    }
}
