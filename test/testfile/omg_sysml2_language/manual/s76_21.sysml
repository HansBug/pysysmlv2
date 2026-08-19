item def Super {
    private package N {
        item def Sub specializes Super;
    }
    item f : N::Sub;
}
