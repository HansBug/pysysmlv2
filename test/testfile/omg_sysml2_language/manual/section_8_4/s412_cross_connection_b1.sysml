item def T1 {
    ref item e2_cross[0..1] : T2;
}
item def T2 {
    ref item e1_cross[1..4] nonunique ordered : T1;
}
connection def B1 {
    end ref e1 : T1 crosses e2.e1_cross;
    end ref e2 : T2 crosses e1.e2_cross;
}
