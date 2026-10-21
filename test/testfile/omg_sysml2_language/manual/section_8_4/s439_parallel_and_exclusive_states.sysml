state def SE specializes States::StateAction {
    state se1 subsets States::StateAction::exclusiveStates;
    state se2 subsets States::StateAction::exclusiveStates;
}
state def SP specializes States::StateAction parallel {
    state sp1 subsets States::StateAction::substates;
    state sp2 subsets States::StateAction::substates;
}
