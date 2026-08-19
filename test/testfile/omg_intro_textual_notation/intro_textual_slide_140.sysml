standard library package VectorFunctions {
    ...
    public import VectorValues::*;
    abstract function isZeroVector {in v: VectorValue[1]; return : Boolean[1];}
    abstract function '+' specializes DataFunctions::'+'
    {in v: VectorValue[1]; in w: VectorValue[0..1]; return u: VectorValue[1];}
    abstract function '-' specializes DataFunctions::'-'
    {in v: VectorValue[1]; in w: VectorValue[0..1]; return u: VectorValue[1];}
    function VectorOf {in components: NumericalValue[1..*] ordered nonunique;
        return : NumericalVectorValue[1];}

    abstract function scalarVectorMult specializes DataFunctions::'*'
    {in x: NumericalValue[1]; in v: NumericalVectorValue[1]; return w: NumericalVectorValue[1];
        alias '*' for scalarVectorMult;
        abstract function vectorScalarMult specializes DataFunctions::'*'
        {in v: NumericalVectorValue[1]; in x: NumericalValue[1]; return : NumericalVectorValue[1];}
        abstract function vectorScalarDiv specializes DataFunctions::'/'
        {in v: NumericalVectorValue[1]; in x: NumericalValue[1]; return : NumericalVectorValue[1];}
        abstract function inner specializes DataFunctions::'*'
        {in v: NumericalVectorValue[1]; in w: NumericalVectorValue[1]; return x: NumericalValue[1];}
        abstract function norm {in v: NumericalVectorValue[1]; return l : NumericalValue[1];}
        abstract function angle {in v: NumericalVectorValue[1]; in w: NumericalVectorValue[1];
            return theta: NumericalValue[1];}
        ...
    }
