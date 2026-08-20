// A use case definition defines a required interaction between its subject and certain external actors.
use case def 'Provide Transportation' {
    subject vehicle : Vehicle;
    // An actor is a parameter of the use case representing a role played by entity external to the subject.
    actor driver : Person;
    // Actors are (referential) part usages and so must have part definitions.
    actor passengers : Person[0..4];
    actor environment : Environment;
    // The objective of the use case is for the subject to provide a result of value to one or more of the actors.
    objective {
        doc /* Transport driver and passengers from
        * starting location to ending location.
        */
    }
}
// Actors may also be specified for other kinds of cases and for requirements.
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
