// The International System of Units defines base units for the seven abstract ISQ unit types.
standard library package SI {
    public import ISQ::*;
    public import SIPrefixes::*;
    // Each unit declaration includes the full unit name and its abbreviation as an identifier.
    attribute <g> gram : MassUnit;
    attribute <m> metre : LengthUnit;
    attribute <kg> kilogram : MassUnit {
        // A unit can be defined using prefix-based conversion from a reference unit.
        attribute redefines unitConversion : ConversionByPrefix {
            attribute redefines prefix = kilo;
            attribute redefines referenceUnit = g
        }
    }
    attribute <s> second : TimeUnit;
    attribute <A> ampere : ElectricCurrentUnit;
    attribute <K> kelvin : ThermodynamicTemperatureUnit;
    attribute <mol> mole : AmountOfSubstanceUnit;
    attribute <cd> candela : LuminousIntensityUnit;
    ...
    // A derived unit can be defined from an arithmetic expression of other units.
    attribute <N> newton : ForceUnit = kg * m / s ^ 2;
