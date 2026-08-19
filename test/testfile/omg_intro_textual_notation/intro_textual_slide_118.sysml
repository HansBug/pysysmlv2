// Specialized kinds of renderings can be defined in a user model.
rendering asTextualNotationTable :> asElementTable {
    view :>> columnView[1] {
        render asTextualNotation;
    }
}
view 'vehicle tabular views' {
    view 'safety features view' : 'Part Structure View' {
        // Views can specify additional filtering conditions on an expose, using the same notation as for an import.
        expose vehicle::**[@Safety];
        render asElementTable;
    }
    view 'non-safety features view' : 'Part Structure View' {
        expose vehicle::**[not (@Safety)];
        render asElementTable;
    }
}
