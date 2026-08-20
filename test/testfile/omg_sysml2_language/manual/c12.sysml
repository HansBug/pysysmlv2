part def Part1 {
  part part2 : Part2 {
    part part4 : Part4;
  }
  part part3 : Part3 {
    part part5 : Part5;
  }
  connection connection1 : ConnectionDef1
    connect part2.part4 to part3.part5;
}
