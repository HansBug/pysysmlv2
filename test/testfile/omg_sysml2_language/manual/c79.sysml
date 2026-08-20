action {
  inout attribute a : Integer;
  action ifThenAction if a < 0 {
    assign a := -a;
  }
}
