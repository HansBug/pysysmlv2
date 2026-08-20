occurrence {
  part part1 : Part1 {
    event occurrence ev1;
  }
  part part2 : Part2 {
    event occurrence ev2;
  }
  message msg1 from part1.ev1 to part2.ev2;
}
