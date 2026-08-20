action action1:Action1 {
  out item1:Item1;
}
action action2:Action2 {
  in item1:Item1;
}
flow action1.item1 to action2.item1;
