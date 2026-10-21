action def AC {
    action a1 { out ref test : ScalarValues::Boolean; }
    succession sc first a1 if a1.test then a2;
    action a2;
}
