constraint def Cst specializes Constraints::ConstraintCheck {
    in attribute x : ScalarValues::Real subsets Base::dataValues;
    // Implied binding between the inherited result parameter
    // and the result of the Expression x > 0.
    x > 0
}
