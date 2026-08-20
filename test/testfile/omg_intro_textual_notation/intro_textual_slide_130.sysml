standard library package NumericalFunctions {
    public import ScalarValues::*;
    function abs {in x: NumericalValue[1]; return : NumericalValue[1];}
    abstract function '+' specializes ScalarFunctions::'+'
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : NumericalValue[1];}
    abstract function '-' specializes ScalarFunctions::'-'
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : NumericalValue[1];}
    abstract function '*' specializes ScalarFunctions::'*'
    {in x: NumericalValue[1]; in y: NumericalValue[1]; return : NumericalValue[1];}
    abstract function '/' specializes ScalarFunctions::'/'
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : NumericalValue[1];}
    abstract function '**' specializes ScalarFunctions::'**'
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : NumericalValue[1];}
    abstract function '^' specializes ScalarFunctions::'^'
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : NumericalValue[1];}
    abstract function '%' specializes ScalarFunctions::'%'
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : NumericalValue[1];}
    abstract function '<'specializes ScalarFunctions::'<'
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : Boolean[1];}
    abstract function '>' specializes ScalarFunctions::'>'
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : Boolean[1];}
    abstract function '<=' specializes ScalarFunctions::'<='
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : Boolean[1];}
    abstract function '>=' specializes ScalarFunctions::'>='
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : Boolean[1];}
    abstract function max specializes ScalarFunctions::max
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : NumericalValue[1];}
    abstract function min specializes ScalarFunctions::min
    {in x: NumericalValue[1]; in y: NumericalValue[0..1]; return : NumericalValue[1];}
    abstract function sum {in collection: NumericalValue[0..*] ordered; return : NumericalValue[1];}
    abstract function product {in collection: NumericalValue[0..*] ordered; return : NumericalValue[1];}
}
