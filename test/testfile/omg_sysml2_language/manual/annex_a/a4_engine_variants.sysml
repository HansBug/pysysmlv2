part engine : Engine {
    part cylinders : Cylinder [4..8] ordered;
}
part engine4Cyl :> engine {
    part redefines cylinders[4];
    part cylinder1[1] subsets cylinders;
    part cylinder2[1] subsets cylinders;
    part cylinder3[1] subsets cylinders;
    part cylinder4[1] subsets cylinders;
}
