standard library package StringFunctions {
    public import ScalarValues::*;
    function '+' specializes ScalarFunctions::'+'
    {in x: String; in y: String; return : String;}
    function Size {in x: String; return : Natural;}
    function Substring
    {in x: String; in lower: Integer; in upper: Integer; return : String;}
    function '<' specializes ScalarFunctions::'<'
    {in x: String; in y: String; return : Boolean;}
    function '>' specializes ScalarFunctions::'>'
    {in x: String; in y: String; return : Boolean;}
    function '<=' specializes ScalarFunctions::'<='
    {in x: String; in y: String; return : Boolean;}
    function '>=' specializes ScalarFunctions::'>='
    {in x: String; in y: String; return : Boolean;}
    function '=' specializes BaseFunctions::'=='
    {in x: String; in y: String; return : Boolean;}
    function ToString specializes BaseFunctions::ToString
    {in x: String; return : String;
    }
