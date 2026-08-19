standard library package QuantityCalculations {
    private import ScalarValues::*;
    private import Quantities::ScalarQuantityValue;
    private import MeasurementReferences::ScalarMeasurementReference;
    private import MeasurementReferences::DimensionOneValue;

    calc def '[' specializes BaseFunctions::'[' { in num: Number[1]; in mRef: ScalarMeasurementReference[1];
        return quantity : ScalarQuantityValue[1]; }
    ...
    calc def abs specializes NumericalFunctions::abs
    { in x: ScalarQuantityValue[1]; return : ScalarQuantityValue[1]; }
    calc def '+' specializes NumericalFunctions::'+'
    { in x: ScalarQuantityValue[1]; in y: ScalarQuantityValue[0..1]; return : ScalarQuantityValue; }
    calc def '-' specializes NumericalFunctions::'-'
    { in x: ScalarQuantityValue; in y: ScalarQuantityValue[0..1]; return : ScalarQuantityValue[1]; }
    calc def '*' specializes NumericalFunctions::'*'
    { in x: ScalarQuantityValue[1]; in y: ScalarQuantityValue[1]; return : ScalarQuantityValue[1]; }
    calc def '/' specializes NumericalFunctions::'/'
    { in x: ScalarQuantityValue[1]; in y: ScalarQuantityValue[1]; return : ScalarQuantityValue[1]; }
    calc def '**' specializes NumericalFunctions::'**'
    { in x: ScalarQuantityValue[1]; in y: Real[1]; return : ScalarQuantityValue[1]; }
    calc def '^' specializes NumericalFunctions::'^'
    { in x: ScalarQuantityValue[1]; in y: Real[1]; return : ScalarQuantityValue[1]; }
    calc def '<' specializes NumericalFunctions::'<'
    { in x: ScalarQuantityValue[1]; in y: ScalarQuantityValue[1]; return : Boolean[1]; }
    calc def '>' specializes NumericalFunctions::'>'
    { in x: ScalarQuantityValue[1]; in y: ScalarQuantityValue[1]; return : Boolean[1]; }
    calc def '<=' specializes NumericalFunctions::'<='
    { in x: ScalarQuantityValue[1]; in y: ScalarQuantityValue[1]; return : Boolean[1]; }
    calc def '>=' specializes NumericalFunctions::'>='
    { in x: ScalarQuantityValue[1]; in y: ScalarQuantityValue[1]; return : Boolean[1]; }
    ...
}
