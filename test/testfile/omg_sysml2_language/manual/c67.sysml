item def ItemDef1 {
  in item 'item1.1';
  out item 'item1.2';
  in item 'item1.3';
}
action action1 {
  inout param1 :ItemDef1;
  out param2 : ItemDef2;
}
