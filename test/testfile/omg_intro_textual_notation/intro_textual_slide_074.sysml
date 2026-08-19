package MassRollup2 {
    private import ScalarFunctions::*;
    part def MassedThing {
        attribute simpleMass :> ISQ::mass;
        // A default value is a feature value that applies unless explicitly overridden.
        attribute totalMass :> ISQ::mass default simpleMass;
    }
    part compositeThing : MassedThing {
        part subcomponents: MassedThing[*];
        // A default value can be overridden when the feature is redefined, with a default or bound value.
        // Once bound, the value of the feature is fixed as the result of the value expression.
        attribute :>> totalMass default mass + sum(subcomponents.totalMass);
    }

    part filteredMassThing :> compositeThing {
        attribute minMass : ISQ::mass
        attribute :>> totalMass =
        // A dot can be followed by a select expression in order to filter a collection of values.
        sum(subcomponents.totalMass.?{in p:>ISQ::mass; p >= minMass)});
    }
}
