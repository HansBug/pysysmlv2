action def A specializes Actions::Action {
    action a1 : A1 subsets Actions::Action::subactions;
    action a2 : A2 subsets Actions::Action::subactions;
    flow subsets Flows::flows, Actions::Action::subactions
        from a1.a1_out to a2.a2_in;
}
