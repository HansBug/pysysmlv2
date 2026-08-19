part def PartDef1 {
    part part2 : Part2
        [0..*];
}

part part1 : Part1
    [0..1] {
    part part2 : Part2
        [0..*];
}

part part1 : Part1
    [0..1] {
    ref part part2 : Part2
        [0..*];
}
