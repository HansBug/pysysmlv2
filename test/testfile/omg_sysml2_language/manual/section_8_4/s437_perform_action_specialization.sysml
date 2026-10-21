action def APA specializes Actions::Action {
    perform action pa1 references act
        subsets Performances::Performance::enclosedPerformances;
    perform action pa2 subsets Actions::actions
        subsets Performances::Performance::enclosedPerformances;
}
