package Accepting {
    action aa1 : AA[1] subsets Action::actions {
        // acpt.receiver == aa1
    }
    part p subsets Parts::parts {
        action aa2: AA[1] subsets Parts::Part::ownedActions {
            // acpt.receiver == p
        }
    }
}
