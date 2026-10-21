action counter {
// This attribute is initialized using a feature value.
attribute count : Natural := 0;
// The target of the following assign action usage is
// implicitly the action "counter".
assign count := count + 1;
// ...
}
