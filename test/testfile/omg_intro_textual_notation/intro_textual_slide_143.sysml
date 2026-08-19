standard library package OccurrenceFunctions {
    ...
    // Test whether two occurrences represent different portions of the same entity (i.e., whether they have the same "identity").
    // Can be invoked using the === operator.
    function '==='  specializes BaseFunctions::'===' {
        in x: Occurrence[0..1]; in y: Occurrence[0..1];
        return : Boolean[1];
    }
    // Test whether a performance of this function happens during the input occurrence.
    function isDuring {
        in occ: Occurrence[1];
        return : Boolean[1];
    }
    // Create or destroy an occurrence.
    function create {
        inout occ: Occurrence[1];
        return : Occurrence[1];
    }
    function destroy {
        inout occ: Occurrence[0..1];
        return : Occurrence[0..1];
    }
    // Add a newly created instance to a group of occurrences.
    function addNew {
        inout group: Occurrence[0..*] nonunique; inout occ: Occurrence[1];
        return : Occurrence[1];
    }
    function addNewAt {
        inout group: Occurrence[0..*] ordered nonunique; inout occ: Occurrence[1]; in index: Positive[1];
        return : Occurrence[1];
    }
    // Remove an instance from a group of occurrences and destroy it.
    behavior removeOld {
        inout group: Occurrence[0..*] nonunique; inout occ: Occurrence[0..1];
    }
    behavior removeOldAt {
        inout group: Occurrence[0..*] ordered nonunique; in index: Positive[1];
    }
}
