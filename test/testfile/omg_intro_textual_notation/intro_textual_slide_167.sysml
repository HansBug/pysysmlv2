// The International System of Quantities defines seven abstract units (length, mass, time, electric current, temperature, amount of substance, luminous intensity) and many other units derived from those.
standard library package ISQ {
    import ISQBase::*;
    import ISQSpaceTime::*;
    ...
}
standard library package ISQBase {
    // A length unit is a simple unit.
    attribute def LengthUnit :> SimpleUnit {...}
    // A length value is a quantity value with a real magnitude and a length-unit scale.
    attribute def LengthValue :> ScalarQuantityValue {
        attribute redefines num : ScalarValues::Real;
        attribute redefines mRef : LengthUnit;
    }
    // A length is a quantity with a length value.
    attribute length: LengthValue :> quantity;
    ...
}
// The ISQ standard (ISO 80000) is divided into several parts. For example, Part 3 defines units related to space and time.
package ISQSpaceTime {
    import ISQBase::*;
    ...
}
