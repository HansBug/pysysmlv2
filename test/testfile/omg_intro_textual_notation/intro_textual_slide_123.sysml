standard library package Collections {
    ...
    datatype KeyValuePair {
        feature key: Anything[0..*] ordered nonunique;
        feature val: Anything[0..*] ordered nonunique;
    }
    datatype Map :> Collection {
        feature :>> elements: KeyValuePair[0..*];
    }
    datatype OrderedMap :> Map {
        feature :>> elements: KeyValuePair[0..*] ordered;
    }
}
