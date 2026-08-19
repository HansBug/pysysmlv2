standard library package RealFunctions {
    public import ScalarValues::*;
    function abs specializes ComplexFunctions::abs {in x: Real[1]; return : Real[1];}
    function '+' specializes ComplexFunctions::'+' {in x: Real[1]; in y: Real[0..1]; return: Real[1];}
    function '-' specializes ComplexFunctions::'-' {in x: Real[1]; in y: Real[0..1]; return: Real[1];}
    function '*' specializes ComplexFunctions::'*' {in x: Real[1]; in y: Real[1]; return: Real[1];}
    function '/' specializes ComplexFunctions::'/' {in x: Real[1]; in y: Real[0..1]; return: Real[1];}
    function '**' specializes ComplexFunctions::'**' {in x: Real[1]; in y: Real[0..1]; return: Real[1];}
    function '^' specializes ComplexFunctions::'^' {in x: Real[1]; in y: Real[0..1]; return: Real[1];}
    function '<' specializes ComplexFunctions::'<'
    {in x: Real[1]; in y: Real[0..1]; return: Boolean[1];}
    function '>' specializes ComplexFunctions::'>'
    {in x: Real[1]; in y: Real[0..1]; return: Boolean[1];}
    function '<=' specializes ComplexFunctions::'<='
    {in x: Real[1]; in y: Real[0..1]; return: Boolean[1];}
    function '>=' specializes ComplexFunctions::'>='
    {in x: Real[1]; in y: Real[0..1]; return: Boolean[1];}
    function max specializes ComplexFunctions::max {in x: Real[1]; in y: Real[0..1]; return: Real[1];}
    function min specializes ComplexFunctions::min {in x: Real[1]; in y: Real[0..1]; return: Real[1];}
    function '==' specializes ComplexFunctions::'=='
    {in x: Real[1]; in y: Real[0..1]; return: Boolean[1];}
    function sqrt {in x: Real[1]; return : Real[1];}
    function floor {in x: Real[1]; return : Integer[1];}
    function round {in x: Real[1]; return : Integer[1];}
    function ToString specializes ComplexFunctions::ToString {in x: Real[1]; return : String[1];}
    function ToInteger {in x: Real[1]; return : Integer[1];}
    function ToRational {in x: Real[1]; return : Rational[1];}
    function ToReal {in x: String[1]; return : Real[1];}
    function ToComplex(x: Real[1]): Complex;
    function sum specializes ComplexFunctions::sum {in collection: Real[0..*]; return : Real[1];}
    function product specializes ComplexFunctions::product {in collection: Real[0..*]; return : Real[1];}
}
