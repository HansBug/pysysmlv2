package Pkg {
    action def A specializes Actions::Action {
        action b subsets Actions::Action::subactions;
    }
    action a1 : A[1] subsets Action::actions {
        // a1.this == a1
        // b.x == a1
    }
    part p subsets Parts::parts {
        action a2: A[1] subsets Parts::Part::ownedActions {
            // a2.this == p
            // b.this == p
        }
    }
}
