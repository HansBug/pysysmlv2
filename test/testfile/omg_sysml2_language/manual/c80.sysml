action {
  in attribute a : Integer;
  out attribute b : Integer;
  action ifThenElseAction if a >= 20 {
    assign b := 100;
  } else {
    assign b := 0;
  }
}
