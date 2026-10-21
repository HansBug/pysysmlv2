state def SA specializes States::StateAction {
    entry action entAct redefines States::StateAction::entryAction;
    do action doAct redefines States::StateAction::doAction;
    exit action extAct redefines States::StateAction::exitAction;
}
