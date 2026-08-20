action action1 : Action1 {
  in input1;
  bind input1 = action2.input2;
  action action2 : Action2 {
    in input2;
    out output2;
  }
  flow action2.output2 to action3.input3;
  action action3 : Action3 {
    in input3;
    out output3;
  }
  bind action3.output3 = output1;
  out output1;
}
