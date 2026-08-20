standard library package BooleanFunctions {
    public import ScalarValues::*;
    function 'not' specializes ScalarFunctions::'not'
    {in x: Boolean; return : Boolean;}
    function 'xor' specializes ScalarFunctions::'xor'
    {in x: Boolean; in y: Boolean; return : Boolean;}
    function '|' specializes ScalarFunctions::'|'
    {in x: Boolean; in y: Boolean; return : Boolean;}
    function '&' specializes ScalarFunctions::'&'
    {in x: Boolean; in y: Boolean; return : Boolean;}
    function '==' specializes BaseFunctions::'=='
    {in x: Boolean; in y: Boolean; return : Boolean;}
    function ToString specializes BaseFunctions::ToString
    {in x: Boolean; return : String;}
    function ToBoolean(x: String): Boolean;
    {in x: String; return : Boolean;}
}
