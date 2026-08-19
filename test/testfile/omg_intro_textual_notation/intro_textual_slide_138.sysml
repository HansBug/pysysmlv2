standard library package SequenceFunctions {
    ...
    function head {in seq: Anything[0..*] ordered nonunique;
        return : Anything[0..1];
    }
    function tail {in seq: Anything[0..*] ordered nonunique ;
        return : Anything[0..*] ordered nonunique;
    }
    function last {in seq: Anything[0..*] ;
        return : Anything[0..1];
    }
    function '#' specializes BaseFunctions::'#' {
        in seq: Anything[0..*] ordered nonunique; in index: Natural[1]; return : Anything[0..1];
    }
    behavior add {
        inout seq: Anything[0..*] ordered nonunique; in values: Anything[0..*] ordered nonunique;
    }
    behavior addAt {
        inout seq: Anything[0..*] ordered nonunique; in values: Anything[0..*] ordered nonunique;
        in index: Positive[1];
    }
    behavior remove{
        inout seq: Anything[0..*] ordered nonunique; in values: Anything[0..*];
    }
    behavior removeAt{
        inout seq: Anything[0..*] ordered nonunique;
        in startIndex: Positive[1]; in endIndex: Positive[1] default startIndex;
    }
}
