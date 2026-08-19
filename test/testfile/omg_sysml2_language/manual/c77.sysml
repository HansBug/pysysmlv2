action actionWithLoop2 {
  in attribute x:Integer;
  out attribute y:Integer;
  attribute increment:Integer = 1;
  first start;
  then assign y := 0;
  then action loop2
  while x < 10 {
    assign y := 2*x;
    then assign x := x + increment;
  }
  then done;
}
