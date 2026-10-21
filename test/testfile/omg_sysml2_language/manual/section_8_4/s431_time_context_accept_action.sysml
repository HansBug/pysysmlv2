part def TimeContext specializes Parts::Part {
    ref redefines localClock = new Time::Clock();
    action behavior subsets Parts::Part::ownedActions {
        // Uses the value bound to TimeContext::localClock,
        // not the default universalClock.
        action subsets Actions::Action::acceptSubactions
            accept after 30 [SI::s];
    }
}
