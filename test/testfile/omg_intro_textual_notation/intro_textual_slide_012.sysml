part def Vehicle {
    // The default multiplicity for parts is 1..1.
    part eng : Engine;
}
part def SmallVehicle :> Vehicle {
    // A specialized definition can redefine a feature that would otherwise be inherited, to change its name and/or specialize its type.
    part smallEng : SmallEngine redefines eng;
}
part def BigVehicle :> Vehicle {
    // The :>> symbol is equivalent to the redefines keyword.
    part bigEng : BigEngine :>> eng;
}
part def Engine {
    // A feature can also specify multiplicity.
    part cyl : Cylinder[4..6];
}
part def SmallEngine :> Engine {
    // There is shorthand notation for redefining a feature with the same name.
    part redefines cyl[4];
}
part def BigEngine :> Engine {
    // Redefinition can be used to constrain the multiplicity of a feature.
    part redefines cyl[6];
}
part def Cylinder;
