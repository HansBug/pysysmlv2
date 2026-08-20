part def Part1 {
  part part2:part2 {
    ref part part4R:Part4;
  }
  part part3:part3 {
    part part4:Part4;
  }
  bind part2.part4R = part3.part4;
}
