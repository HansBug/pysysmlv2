standard library package ComplexFunctions {
    public import ScalarValues::*;
    feature i: Complex[1] = rect(0.0, 1.0);
    function rect{in re: Real[1]; in im: Real[1]; return : Complex[1];}
    function polar{in abs: Real[1]; in arg: Real[1]; return : Complex[1];}
    function re{in x: Complex[1]; return : Real[1];}
    function im {in x: Complex[1]; return : Real[1];}
    function abs specializes NumericalFunctions::abs {in x: Complex[1]; return : Real[1];}
    function {in x: Complex[1]; return : Real[1];}
    function '+' specializes NumericalFunctions::'+'
    {in x: Complex[1]; in y: Complex[0..1]; return : Complex[1];
        function '-' specializes NumericalFunctions::'-'
        {in x: Complex[1]; in y: Complex[0..1]; return : Complex[1];
            function '*' specializes NumericalFunctions::'*'
            {in x: Complex[1]; in y: Complex[1]; return : Complex[1];
                function '/' specializes NumericalFunctions::'/'
                {in x: Complex[1]; in y: Complex[1]; return : Complex[1];
                    function '**' specializes NumericalFunctions::'**'
                    {in x: Complex[1]; in y: Complex[1]; return : Complex[1];
                        function '^' specializes NumericalFunctions::'^'
                        {in x: Complex[1]; in y: Complex[1]; return : Complex[1];
                            function '==' specializes DataFunctions::'=='
                            {in x: Complex[1]; in y: Complex[1]; return : Complex[1];
                                function ToString specializes BaseFunctions::ToString {in x: Complex[1]; return : String[1];}
                                function ToComplex {in x: String[1]; return : Complex[1];}
                                function sum specializes NumericalFunctions::sum {in collection: Complex[0..*]; return : Complex[1];}
                                function product specializes NumericalFunctions::product {in collection: Complex[0..*]; return : Complex[1];}
                            }
