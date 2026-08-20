private import ISQ::*;
private import SI::*;
private import ScalarFunctions::*;
constraint def MassConstraint {
    in partMasses : MassValue[0..*];
    in massLimit : MassValue;
    sum(partMasses) <= massLimit
}
part def Vehicle {
    // A constraint assertion asserts that a constraint must be true.
    // If an assertion is violated, then the model is inconsistent.
    assert constraint massConstraint : MassConstraint {
        in partMasses = (chassisMass, engine.mass, transmission.mass);
        in massLimit = 2500[kg];
    }
    attribute chassisMass : MassValue;
    part engine : Engine {
        attribute mass : MassValue;
    }
    part transmission : Engine {
        attribute mass : MassValue;
    }
}
