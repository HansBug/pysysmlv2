standard library package Measurement {
    ...
    // A measurement unit is a measurement scale defined as a sequence of unit power factors.
    abstract attribute def MeasurementUnit
    :> ScalarMeasurementReference {
        attribute unitPowerFactor : UnitPowerFactor[1..*] ordered;
        attribute unitConversion : UnitConversion[0..1];
    }
    // A simple unit is a measurement unit with no power factor dependencies on other units.
    abstract attribute def SimpleUnit :> MeasurementUnit {
        attribute redefines unitPowerFactor[1] {
            attribute redefines unit = SimpleUnit::self;
            attribute redefines exponent = 1;
        }
    }
    // A derived unit is any unit that is not simple.
    abstract attribute def DerivedUnit :> MeasurementUnit;
    // A unit power factor is a representation of a reference unit raised to an exponent.
    attribute def UnitPowerFactor {
        attribute unit : MeasurementUnit;
        attribute exponent : ScalarValues::Real;
    }
    ...
}
