action actionWithLoop3 {
  in attribute n:Integer;
  out attribute y:Integer;
  first start;
  then assign y := 0;
  then action forLoop1
  for i : Integer in 1..n {
    assign y := y + i;
  }
  then done;
}
