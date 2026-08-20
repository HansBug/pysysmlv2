port def Pa {
  port p1 : P1;
  port p2 : P2;
  port p3 : P3;
}
part def Part1 {
  port pa : Pa;
}
part def Part2 {
  port pb : ~Pa;
}
interface def InterfaceDef2 {
  end :>> source : Pa;
  end :>> target : ~Pa;
}
part part0 {
  part part1 : Part1;
  part part2 : Part2;

  interface interface2 : InterfaceDef2
    connect source ::> part1.pa to target ::> part2.pb {
      interface source.p1 to target.p1;
      interface source.p2 to target.p2;
      interface source.p3 to target.p3;
    }
}
