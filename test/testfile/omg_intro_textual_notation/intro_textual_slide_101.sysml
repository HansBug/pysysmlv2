use case 'provide transportation' : 'Provide Transportation' {
    subject vehicle;
    first start;
    then include use case 'enter vehicle' : 'Enter Vehicle' {
        subject vehicle;
        actor :>> driver = 'provide transportation'::driver;
        actor :>> passengers = 'provide transportation'::passengers;
    }
    then use case 'drive vehicle' {
        subject vehicle;
        actor driver = 'provide transportation'::driver;
        actor environment = 'provide transportation'::environment;
        include 'add fuel'[0..*] {
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
use case 'add fuel' {
    subject vehicle : Vehicle;
    actor fueler : Person;
    actor 'fuel station' : 'Fuel Station';
}
