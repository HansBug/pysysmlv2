standard library package VectorCalculations {
    private import ScalarValues::Boolean;
    private import ScalarValues::Number;
    private import Quantities::VectorQuantityValue;
    calc def '+' specializes VectorFunctions::'+'
    {in : VectorQuantityValue; in : VectorQuantityValue; return : VectorQuantityValue;}
    calc def '-' specializes VectorFunctions::'-'
    {in : VectorQuantityValue; in : VectorQuantityValue; return : VectorQuantityValue;}
    calc def scalarVectorMult specializes VectorFunctions:: scalarVectorMult
    {in : Number; in : VectorQuantityValue; return : VectorQuantityValue;}
    calc def vectorScalarMult specializes VectorFunctions:: vectorScalarMult
    {in : VectorQuantityValue; in : Number; return : VectorQuantityValue;}
    calc def vectorScalarDiv specializes RealFunctions::'*'
    {in : VectorQuantityValue; in : Number; return : VectorQuantityValue;}
    calc def inner specializes VectorFunctions::inner
    {in : VectorQuantityValue; in : VectorQuantityValue; return : Number;}
    alias scalarVectorMult as '*';
    calc def norm specializes VectorFunctions::norm
    {in : VectorQuantityValue; return : Number;}
    calc def angle specializes VectorFunctions::angle
    {in : VectorQuantityValue; in : VectorQuantityValue; return : Number;}
}
