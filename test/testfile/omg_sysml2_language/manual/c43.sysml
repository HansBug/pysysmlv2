port def Pa {
  out item i1Out : Item1;
  in item i2In : Item2;
}
interface def Interface2 {
  end supplierP : Pa;
  end consumerP : ~Pa;
  flow supplierP.i1Out to consumerP.i1Out;
  flow consumerP.i2In to supplierP.i2In;
}
part part0 {
  part part1 : Part1 {
    port pa : Pa;
  }
  part part2 : Part2 {
    port pb : ~Pa;
  }
  interface if2 : Interface2 connect part1.pa to part2.pb;
}
