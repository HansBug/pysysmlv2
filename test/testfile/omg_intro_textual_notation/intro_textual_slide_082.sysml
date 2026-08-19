// The constraint expression can also be defined on a usage of a constraint def.
constraint def MassConstraint {
    in partMasses : MassValue[0..*];
    in massLimit : MassValue;
}
constraint massConstraint : MassConstraint {
    sum(partMasses) <= massLimit
}
part def Vehicle {
    // A named constraint can be asserted in multiple contexts.
    assert massConstraint  {
        in partMasses = (chassisMass, engine.mass, transmission.mass);
        in massLimit = 2500[kg];
    }
    attribute chassisMass : MassValue;
    attribute engine : Engine {
        value mass : MassValue;
    }
    attribute transmission : Engine {
        value mass : MassValue;
    }
}
