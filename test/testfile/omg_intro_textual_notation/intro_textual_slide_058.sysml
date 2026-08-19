part def Vehicle {
    ...
    snapshot delivery {
        attribute deliveryDate : Date;
    }
    // This is a shorthand for a succession after the lexically previous occurrence.
    then timeslice ownership[0..*] ordered {
        // start is the name of the start-of-life snapshot of any occurrence.
        snapshot sale = start;
        // One occurrence references another during the same time period in the other reference's lifetime.
        ref item owner : Person[1];
        // Time slices and snapshots can have nested time slices, snapshots and other features applicable during their occurrence.
        timeslice driven[0..*] {
            ref item driver : Person[1];
        }
    }
    snapshot junked = done;
}
