constraint assumption1 { /*...*/ }
constraint constraint1 { /*...*/ }
requirement requirement1 {
    assume assumption1;
    assume constraint assumption2 { /*...*/ }
    require constraint1;
}
