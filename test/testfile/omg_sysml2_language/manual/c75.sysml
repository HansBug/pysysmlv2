action actionWithLoop1 {
  attribute x:Integer;
  attribute increment:Integer = 1;
  attribute y:Integer;
  first start;
  then assign x := 1;
  then action loop1
  loop {
    assign y := 2*x;
    then assign x := x + increment;
  } until x >= 10;
  then done;
}
