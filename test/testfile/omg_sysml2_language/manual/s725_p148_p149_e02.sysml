use case 'provide transportation' : 'Provide Transportation' {
    first start;

    then include 'enter vehicle' {
        actor :>> driver = 'provide transportation'::driver;
        actor :>> passengers = 'provide transportation'::passengers;
    }

    then include 'drive vehicle' {
        actor :>> driver = 'provide transportation'::driver;
        actor :>> environment = 'provide transportation'::environment;
    }

    then include 'exit vehicle' {
        actor :>> driver = 'provide transportation'::driver;
        actor :>> passengers = 'provide transportation'::passengers;
    }

    then done;
}
