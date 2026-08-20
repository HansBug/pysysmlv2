private import ScalarValues::*;
private import MassRollup2::*;
// The default of totalMass to simpleMass is inherited.
part def CarPart :> MassedThing {
    attribute serialNumber : String;
}
// The default for totalMass is overridden as specified in compositeThing.
part car: CarPart :> compositeThing {
    attribute vin :>> serialNumber;
    // The totalMass default is not overridden for the nested carParts.
    part carParts : CarPart[*] :>> subcomponents;
    part engine :> carParts { ... }
    part transmission :> carParts { ... }
}
// Example usage
private import SI::kg;
// When computing the totalMass of c, c.engine and c.transmission, the relevant defaults are used.
part c :> car {
    attribute :>> simpleMass = 1000[kg];
    part :>> engine {
        attribute :>> simpleMass = 100[kg];
    }
    part attribute transmission {
        attribute :>> simpleMass = 50[kg];
    }
}
// c.totalMass --> 1150.0[kg]
