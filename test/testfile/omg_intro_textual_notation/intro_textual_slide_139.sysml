standard library package CollectionFunctions {
    ...
    public import Collections::*;
    function '==' specializes BaseFunctions::'=='
    {in col1: Collection[0..1]; in col2: Collection[0..1]; return : Boolean[1];}
    function size {in col: Collection[1]; return : Natural[1];}
    function isEmpty {in col: Collection[1]; return : Boolean[1];}
    function notEmpty {in col: Collection[1]; return : Boolean[1];}
    function contains {in col: Collection[1]; in values: Anything[*]; return : Boolean[1];}
    function containsAll {in col1: Collection[1]; in col2: Collection[2]; return : Boolean[1];}
    function head {in col: OrderedCollection[1]; return : Anything[0..1];}
    function tail {in col: OrderedCollection[1]; return : Anything[0..*] ordered nonunique;}
    function last {in col: OrderedCollection[1]; return : Anything[0..1];}
    function '#' specializes BaseFunctions::'#'
    {in col: OrderedCollection[1]; in index: Positive[1]; return : Anything[0..1];}
    function 'array#' specializes BaseFunctions::'#'
    {in arr: Array[1]; in indexes: Positive[n] ordered nonunique; return : Anything[0..1];}
}
