part part1 : Part1 {
    port p1 : P1Def;
    port p6 : P6Def;

    part part2 : Part2;
    part part3 : Part3;

    bind p1 = part2.p2;
    connect part2.p3 to part3.p4;
    bind part2.p5 = p6;
}
