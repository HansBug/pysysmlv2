use case 'provide transportation' : 'Provide Transportation' {
    subject vehicle;
    // The required behavior of a use case can be specified as for an action.
    first start;
    then include use case 'enter vehicle' : 'Enter Vehicle' {
        subject vehicle;
        actor :>> driver = 'provide transportation'::driver;
        actor :>> passengers = 'provide transportation'::passengers;
    }
    // A use case can define sub-use cases within its behavior.
    // The traditional use case “extend” relationship is not supported yet.
    then use case 'drive vehicle' {
        subject vehicle;
        actor driver = 'provide transportation'::driver;
        actor environment = 'provide transportation'::environment;
        include 'add fuel'[0..*] {
            // A subject must be declared first, before any actors. It can only be omitted if there are no actors or other parameters.
            subject vehicle;
            actor :>> fueler = driver;
        }
    }
    // A use case can include the performance of a use case defined elsewhere (similar to performing an action).
    // The subject of a nested use case is implicitly bound to that of its containing use case, but actors need to be explicitly bound.
    then include use case 'exit vehicle' : 'Exit Vehicle' {
        subject vehicle;
        actor :>> driver = 'provide transportation'::driver;
        actor :>> passengers = 'provide transportation'::passengers;
    }
    then done;
}
// A use case can also be specified without an explicit use case definition.
use case 'add fuel' {
    subject vehicle : Vehicle;
    actor fueler : Person;
    actor 'fuel station' : 'Fuel Station';
}
