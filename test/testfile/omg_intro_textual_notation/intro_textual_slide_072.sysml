package MassRollup1 {
    private import ScalarFunctions::*;
    part def MassedThing {
        // ISQ::mass is a standard quantity kind from the International System of Quantities library model.
        attribute simpleMass :> ISQ::mass;
        attribute totalMass :> ISQ::mass;
    }
    part simpleThing : MassedThing {
        // A feature value is a shorthand for binding a feature to the result of an expression (here simply the value of another feature).
        attribute :>> totalMass = simpleMass;
    }
    part compositeThing : MassedThing {
        part subcomponents: MassedThing[*];
        attribute :>> totalMass =
        // An expression in general is a computation expressed using a typical mathematical operator notation.
        // The dot notation can be used as an expression to read the values of a feature. Here, the totalMass is collected for each of the subcomponents.
        simpleMass + sum(subcomponents.totalMass);
    }
}
