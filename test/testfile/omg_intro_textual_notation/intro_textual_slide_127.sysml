// ScalarFunctions package is similar but specialized for ScalarValue.
standard library package DataFunctions {
    ...
    abstract function '=='specializes BaseFunctions::'=='
    {in x: DataValue[0..1]; in y: DataValue[0..1]; return : Boolean[1];}
    function '==='specializes BaseFunctions::'==='
    {in x: DataValue[0..1]; in y: DataValue[0..1]; return : Boolean[1];}
    abstract function '+'{in x: DataValue[1]; in y: DataValue[0..1]; return : DataValue[1];}
    abstract function '-'{in x: DataValue[1]; in y: DataValue[0..1]; return : DataValue[1];}
    abstract function '*'{in x: DataValue[1]; in y: DataValue[1]; return : DataValue[1];}
    abstract function '/'{in x: DataValue[1]; in y: DataValue[1]; return : DataValue[1];}
    abstract function '**'{in x: DataValue[1]; in y: DataValue[1]; return : DataValue[1];}
    abstract function '^'{in x: DataValue[1]; in y: DataValue[1]; return : DataValue[1];}
    abstract function '%'{in x: DataValue[1]; in y: DataValue[1]; return : DataValue[1];}
    abstract function 'not'{in x: DataValue[1]; return : DataValue[1];}
    abstract function 'xor'{in x: DataValue[1]; in y: DataValue[1]; return : DataValue[1];}
    abstract function '~'{in x: DataValue[1]; return : DataValue[1];}
    abstract function '|'{in x: DataValue[1]; in y: DataValue[1]; return : DataValue[1];}
    abstract function '&'{in x: DataValue[1]; in y: DataValue[1]; return : DataValue[1];}
    abstract function '<'{in x: DataValue[1]; in y: DataValue[1]; return : Boolean[1];}
    abstract function '>'{in x: DataValue[1]; in y: DataValue[1]; return : Boolean[1];}
    abstract function '<='{in x: DataValue[1]; in y: DataValue[1]; return : Boolean[1];}
    abstract function '>='{in x: DataValue[1]; in y: DataValue[1]; return : Boolean[1];}
    abstract function max{in x: DataValue[1]; return : DataValue[1];}
    abstract function min{in x: DataValue[1]; return : DataValue[1];}
    abstract function '..'
    {in lower:DataValue[1]; in upper:DataValue[1]; return : DataValue[0..*] ordered;
    }
}
