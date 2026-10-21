constraint cst : Cst subsets Constraints::constraintChecks {
    in ref x redefines Cst::x = 2;
    // Inherits result parameter and result Expression from Cst.
}
