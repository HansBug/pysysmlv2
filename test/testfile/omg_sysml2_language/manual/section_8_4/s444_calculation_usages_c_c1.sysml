calc c : C subsets Calculations::calculations {
    in ref a redefines C::a;
    in ref b redefines C::b;
    return result redefines C::result, Calculation::calculations::result;
}
calc c1 : C1 subsets c {
    return ref result redefines C1::result, c::result;
}
