// A use case definition defines a required interaction between its subject and certain external actors.
use case def 'Provide Transportation' {
    subject vehicle : Vehicle;
    actor driver : Person;
    actor passengers : Person[0..4];
    actor environment : Environment;
    // The objective of the use case is for the subject to provide a result of value to one or more of the actors.
    objective {
        doc /* Transport driver and passengers from
        * starting location to ending location.
        */
    }
}
use case def 'Enter Vehicle' {
    subject vehicle : Vehicle;
    actor driver : Person;
    actor passengers : Person[0..4];
}
use case def 'Exit Vehicle' {
    subject vehicle : Vehicle;
    actor driver : Person;
    actor passengers : Person[0..4];
}
