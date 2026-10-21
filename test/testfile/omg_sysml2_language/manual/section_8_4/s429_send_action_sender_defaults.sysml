package Sending {
    action as1 : AS[1] subsets Action::actions {
        // snd.sender == as1
    }
    part p subsets Parts::parts {
        action as2: AS[1] subsets Parts::Part::ownedActions {
            // snd.sender == p
        }
    }
}
