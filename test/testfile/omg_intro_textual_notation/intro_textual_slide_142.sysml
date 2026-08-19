standard library package ControlFunctions {
    private import Base::Anything;
    private import ScalarValues::ScalarValue;
    abstract function 'if' {in test: Boolean[1];
        in expr thenValue[0..1] {return : Anything[0..*] ordered nonunique;}
        in expr elseValue[0..1] {return : Anything[0..*] ordered nonunique;}
        return : Anything[0..*] ordered nonunique;}
    abstract function '??' {in firstValue: Anything[0..*];
        in expr secondValue[0..1] {return : Anything[0..*] ordered nonunique;}
        return : Anything[0..*] ordered nonunique;}
    function 'and'
    {in firstValue: Anything[0..*]; in expr secondValue[0..1] {return : Boolean[1];} return : Boolean[1];}
    function 'or'
    {in firstValue: Anything[0..*]; in expr secondValue[0..1] {return : Boolean[1];} return : Boolean[1];}
    function 'implies'
    {in firstValue: Anything[0..*]; in expr secondValue[0..1] {return : Boolean[1];} return : Boolean[1];}
    abstract function collect {in collection: Anything[0..*] ordered nonunique;
        in expr mapper[0..*] (argument: Anything[1]): Anything[0..*] ordered nonunique;
        return : Anything[0..*] ordered nonunique {
        }
        abstract function select { in collection: Anything[0..*] ordered nonunique;
            in expr selector[0..*] (argument: Anything[1]): Boolean[1];
            return : Anything[0..*] ordered nonunique {
            }
            abstract function reject { in collection: Anything[0..*] ordered nonunique;
                in expr rejector[0..*] (argument: Anything[1]): Boolean[1];
                return : Anything[0..*] ordered nonunique {
                }
                ...
            }
