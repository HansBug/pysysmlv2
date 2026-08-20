standard library package SequenceFunctions {
    ...
    function equals {in x: Anything[0..*] ordered nonunique; in y: Anything[0..*] ordered nonunique;
        return : Boolean[1];
    }
    function same {in x: Anything[0..*] ordered nonunique; in y: Anything[0..*] ordered nonunique;
        return : Boolean[1];
    }
    function size {in seq: Anything[0..*] nonunique; return : Natural[1];}
    function isEmpty {in seq: Anything[0..*] nonunique; return : Boolean[1];}
    function notEmpty {in seq: Anything[0..*] nonunique; return : Boolean[1];}
    function includes {in seq1: Anything[0..*] nonunique; in seq2: Anything[0..*] nonunique;
        return : Boolean[1];
    }
    function excludes {in seq1: Anything[0..*] nonunique; in seq2: Anything[0..*] nonunique;
        return : Boolean[1];
    }
    function including {in seq: Anything[0..*] ordered nonunique; in values: Anything[0..*] ordered nonunique;
        return : Anything[0..*] ordered nonunique;
    }
    function includingAt{in seq: Anything[0..*] ordered nonunique; in values: Anything[0..*] ordered nonunique;
        in index: Positive[1]; return : Anything[0..*] ordered nonunique;
    }
    function excluding {in seq: Anything[0..*] ordered nonunique; in values: Anything[0..*] ordered nonunique;
        return : Anything[0..*] ordered nonunique;
    }
    function excludingAt{in seq: Anything[0..*] ordered nonunique; in values: Anything[0..*] ordered nonunique;
        in index: Positive[1]; return : Anything[0..*] ordered nonunique;
    }
    ...
