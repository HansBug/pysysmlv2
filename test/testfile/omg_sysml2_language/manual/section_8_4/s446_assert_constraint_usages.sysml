assert constraint ast references cst subsets Constraints::assertedConstraints;
assert constraint ast1 : Cst subsets Constraints::assertedConstraints {
    redefines x = 3;
}
assert not constraint ast2 : Cst subsets Constraints::negatedConstraints {
    redefines x = -3;
}
