calc def C specializes Calculations::Calculation {
    in ref a redefines Base::things;
    in ref b redefines Base::things;
    return ref result redefines Calculations::Calculation::result;
}
calc def C1 specializes C {
    in ref a redefines C::a;
    // The result parameter can be in any position.
    return ref result redefines C::result;
    in ref b redefines C::b;
}
