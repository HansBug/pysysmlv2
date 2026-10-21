case cs : Cs subsets Cases::cases {
    return result redefines Cs::result;
}
case cs1 : Cs1 subsets cs {
    return ref result redefines Cs1::result, cs::result;
}
