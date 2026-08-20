part part1:Part1 {
  port p4:P4;
}
part part2:Part2 {
  port p2:P2;
}
interface interface1 : InterfaceDef1
  connect part1.p4 to part2.p2;
