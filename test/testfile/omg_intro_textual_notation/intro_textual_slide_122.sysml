standard library package Collections {
    ...
    abstract datatype Collection {
        feature elements[0..*] nonunique;
    }
    abstract datatype OrderedCollection :> Collection {
        feature :>> elements[0..*] ordered nonunique;
    }
    abstract datatype UniqueCollection :> Collection {
        feature :>> elements[0..*];
    }
    datatype Array :> OrderedCollection {
        feature dimensions: Positive[0..*] ordered nonunique;
        feature rank: Natural[1] = size(dimensions);
        feature flattenedSize: Positive[1] = dimensions->reduce '*' ?? 1;
        inv { flattenedSize == size(elements) }
    }
    datatype Bag :> Collection;
    datatype Set :> UniqueCollection;
    datatype OrderedSet :> OrderedCollection, UniqueCollection {
        feature :>> elements[0..*] ordered;
    }
    datatype List :> OrderedCollection;
    ...
}
