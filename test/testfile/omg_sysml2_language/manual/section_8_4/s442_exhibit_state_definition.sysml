state def SES specializes States::State {
    exhibit state es1 references st
        subsets Performances::Performance::enclosedPerformances;
    exhibit state es2 subsets State::states
        subsets Performances::Performance::enclosedPerformances;
}
