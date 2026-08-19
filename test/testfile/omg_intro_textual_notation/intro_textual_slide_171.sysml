standard library package QuantityCalculations {
    ...
    calc def max specializes NumericalFunctions::max
    { in x: ScalarQuantityValue[1]; in y: ScalarQuantityValue[1]; return : ScalarQuantityValue[1]; }
    calc def min specializes NumericalFunctions::min
    { in x: ScalarQuantityValue[1]; in y: ScalarQuantityValue[1]; return : ScalarQuantityValue[1]; }
    calc def '==' specializes DataFunctions::'=='
    { in x: ScalarQuantityValue[1]; in y: ScalarQuantityValue[1]; return : Boolean[1]; }
    calc def sqrt{ in x: ScalarQuantityValue[1]; return : ScalarQuantityValue[1]; }
    calc def floor { in x: ScalarQuantityValue[1]; return : ScalarQuantityValue[1]; }
    calc def round { in x: ScalarQuantityValue[1]; return : ScalarQuantityValue[1]; }
    calc def ToString specializes BaseFunctions::ToString { in x: ScalarQuantityValue[1]; return : String; }
    calc def ToInteger { in x: ScalarQuantityValue[1]; return : Integer[1]; }
    calc def ToRational { in x: ScalarQuantityValue[1]; return : Rational[1]; }
    calc def ToReal { in x: ScalarQuantityValue[1]; return : Real[1]; }
    calc def ToDimensionOneValue { in x: Real[1]; return : DimensionOneValue[1]; }
    calc def sum specializes NumericalFunctions::sum
    { in collection: ScalarQuantityValue[0..*]; return : ScalarQuantityValue; }
    calc def product specializes NumericalFunctions::product
    { in collection: ScalarQuantityValue[0..*]; return : ScalarQuantityValue; }
    calc def ConvertQuantity { in x: ScalarQuantityValue[1]; in targetMRef: ScalarMeasurementReference[1];
        return : ScalarQuantityValue[1]; }
}
