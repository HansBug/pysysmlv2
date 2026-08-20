standard library package BaseFunctions {
    private import Base::Anything;
    private import ScalarValues::*;
    abstract function '==' { in x: Anything[0..1]; in y: Anything[0..1];
        return : Boolean[1];
    }
    function '!=' { in x: Anything[0..1]; in y: Anything[0..1];
        return : Boolean[1] = not (x == y)
    }
    abstract function '===' { in x: Anything[0..1]; in y: Anything[0..1];
        return : Boolean[1];
    }
    function '!==' { in x: Anything[0..1]; in y: Anything[0..1];
        return : Boolean[1] = not (x === y)
    }
    function ToString { in Anything[0..1];
        return : String[1];
    }
    abstract function '['{ in x: Anything[0..*] nonunique; in y: Anything[0..*] nonunique;
        return : Anything[0..*] nonunique;
    }
    abstract function '#'{ in seq: Anything[0..*] ordered nonunique; in index: Positive[1..*] ordered nonunique;
        return : Anything[0..1];
    }
    abstract function ','{
        in seq1: Anything[0..*] ordered nonunique; seq2: Anything[0..*] ordered nonunique;
        return : Anything[0..*] ordered nonunique;
    }
    ...
}
