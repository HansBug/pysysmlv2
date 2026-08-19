attribute def Diameter :> Real;
part def Cylinder {
    attribute diameter : Diameter[1];
}
part def Engine {
    part cylinder : Cylinder[2..*];
}
part '4cylEngine' : Engine {
    part redefines cylinder[4];
}
part '6cylEngine' : Engine {
    part redefines cylinder[6];
}
// Variability model
// Any kind of definition can be marked as a variation, expressing variability within a product line model.
// A variation defines one or more variant usages, which represent the allowed choices for that variation.
variation attribute def DiameterChoices :> Diameter {
    variant attribute diameterSmall = 70[mm];
    variant attribute diameterLarge = 100[mm];
}
variation part def EngineChoices :> Engine {
    variant '4cylEngine';
    variant '6cylEngine';
}
