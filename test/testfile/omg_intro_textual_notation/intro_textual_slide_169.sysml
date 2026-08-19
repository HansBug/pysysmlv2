// US customary units are defined by conversion from SI units.
standard library package USCustomaryUnits {
    public import ISQ::*;
    private import SI::*;
    attribute <ft> foot : LengthUnit {
        attribute redefines unitConversion : ConversionByConvention {
            attribute redefines referenceUnit = m,
            attribute redefines conversionFactor = 3048/10000;
        }
    }
    ...
    attribute <mi> mile : LengthUnit {
        attribute redefines unitConversion : ConversionByConvention {
            attribute redefines referenceUnit = ft,
            attribute redefines conversionFactor = 5280;
        }
    }
    attribute <'mi/hr'> 'mile per hour' : SpeedUnit = mi / hr;
    // An alias for mile per hour.
    alias mph for 'mi/hr';
    ...
}
