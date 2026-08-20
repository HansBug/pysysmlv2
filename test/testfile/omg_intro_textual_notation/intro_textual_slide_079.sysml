private import ISQ::*;
private import SI::*;
private import ScalarFunctions::*;
// A constraint definition is a reusable, parameterized Boolean expression.
// A constraint may be violated (false) without making the model inconsistent.
constraint def MassConstraint {
    // Constraint parameters are always in parameters.
    in partMasses : MassValue[0..*];
    in massLimit : MassValue;
    // The constraint expression can be any Boolean expression using the constraint parameters.
    // There is no semicolon at the end of a constraint expression.
    sum(partMasses) <= massLimit
}
part def Vehicle {
    // A constraint is the usage of a constraint definition, which may be true or false in a given context.
    constraint massConstraint : MassConstraint {
        // Values are bound to constraint parameters (similarly to actions).
        in partMasses = (chassisMass, engine.mass, transmission.mass);
        in massLimit = 2500[kg];
    }
    attribute chassisMass : MassValue;
    part engine : Engine {
        attribute mass : MassValue;
    }
    part transmission : Transmission {
        attribute mass : MassValue;
    }
}
