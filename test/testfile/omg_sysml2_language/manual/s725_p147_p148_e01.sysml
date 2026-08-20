use case def 'Provide Transportation' {
    subject vehicle : Vehicle {
        event occurrence driverEnters [1];
        then event occurrence passengerEnters [0..*];
        then event occurrence startsDrive [1];
        then event occurrence endsDrive [1];
        then event occurrence passengerExits [0..*];
        then event occurrence driverExits [1];
    }
    actor driver : Person {
        event occurrence entersVehicle [1];
        then event occurrence exitsVehicle [1];
    }
    actor passengers : Person[0..4] {
        event occurrence entersVehicle [1];
        then event occurrence exitsVehicle [1];
    }
    actor environment : Environment {
        event occurrence vehicleDrives [1];
    }
    objective {
        doc        /* Transport driver and passengers from starting location
         * to ending location.
         */
    }
    message of Enter from driver.entersVehicle to vehicle.driverEnters;
    then message of Enter from passengers.entersVehicle to vehicle.passengerEnters;
    then message of Drive from vehicle.drives to environment.vehicleDrives;
    then message of Exit from passengers.exitsVehicle to vehicle.passengerExits;
    then message of Exit from driver.exitsVehicle to vehicle.driverExits;
}
