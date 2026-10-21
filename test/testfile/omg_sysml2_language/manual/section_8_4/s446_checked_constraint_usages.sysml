item def ICst specializes Items::Item {
    constraint c : Cst subsets Items::Item::checkedConstraints;
}
action def ACst specializes Actions::Action {
    constraint c : Cst subsets Objects::Object::ownedPerformances;
}
