private import ISQ::*;
private import SI::*;
private import ScalarFunctions::*;
constraint def MassConstraint {
    // Alternatively, constraint parameters may be modeled as attribute or reference features.
    attribute partMasses : MassValue[0..*];
    attribute massLimit : MassValue;
    sum(partMasses) <= massLimit
}
part def Vehicle {
    constraint massConstraint : MassConstraint {
        // The constraint parameter properties are then redefined in order to be bound.
        redefines partMasses = (chassisMass, engine.mass, transmission.mass);
        redefines massLimit = 2500[kg];
    }
    attribute chassisMass : MassValue;
    part engine : Engine {
        attribute mass : MassValue;
    }
    part transmission : Engine {
        attribute mass : MassValue;
    }
}
