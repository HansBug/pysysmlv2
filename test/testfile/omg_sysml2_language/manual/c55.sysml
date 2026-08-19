item def Item1 {
  item subItem1;
  item subItem2;
  item subItem3;
}
action action1 : Action1 {
  out item1 : Item1;
}
action action2 : Action2 {
  in item2 : Item1;
}
flow flow1_2 from action1.item1 to action2.item2 {
  flow source.item1.subItem1 to target.item2.subItem1;
  flow source.item1.subItem2 to target.item2.subItem2;
  flow source.item1.subItem3 to target.item2.subItem3;
}
