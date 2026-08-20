private import ScalarValues::*;
private import MassRollup1::*;
part def CarPart :> MassedThing {
    attribute serialNumber : String;
}
part car: CarPart :> compositeThing {
    attribute vin :>> serialNumber;
    part carParts : CarPart[*] :>> subcomponents;
    part engine :> simpleThing, carParts { ... }
    part transmission :> simpleThing, carParts { ... }
}
// Example usage
private import SI::kg;
// The totalMass of c can be computed using the feature value expressions from simpleThing and compositeThing.
part c :> car {
    // This is an expression for a quantity with a specific numeric value and unit. Note that units are identified on the quantity value, not the type.
    attribute :>> simpleMass = 1000[kg];
    part :>> engine {
        attribute :>> simpleMass = 100[kg];
    }
    part attribute transmission {
        attribute :>> simpleMass = 50[kg];
    }
}
// c.totalMass --> 1150.0[kg]
