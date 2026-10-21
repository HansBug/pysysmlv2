item marketSurvey;
dependency from vehicleSpecification to marketSurvey;
requirement vehicleSpecification {
    subject vehicle : Vehicle;
    requirement <'1'> vehicleMassRequirement : MassRequirement {
        doc /* The total mass of a vehicle shall be less than or equal to the required mass.
        Assume total mass includes a full tank of gas of 60 kg*/
        attribute redefines massRequired = 2000[kg];
        attribute redefines massActual = vehicle.dryMass + fuelMassActual;
        attribute fuelMassActual :> ISQ::mass;
        attribute fuelMassMax :> ISQ::mass = 60[kg];
        assume constraint { fuelMassActual == fuelMassMax }
    }
    allocate vehicleMassRequirement to PartsTree::vehicle_b.mass;
    requirement <'2'> vehicleFuelEconomyRequirements {
        doc /* fuel economy requirements group */
        attribute assumedCargoMass :> ISQ::mass;
        requirement <'2_1'> cityFuelEconomyRequirement : FuelEconomyRequirement {
            redefines requiredFuelEconomy = 10[km / L];
            assume constraint { assumedCargoMass >= 500[kg] }
        }
        requirement <'2_2'> highwayFuelEconomyRequirement : FuelEconomyRequirement {
            redefines requiredFuelEconomy = 12.75[km / L];
            assume constraint { assumedCargoMass >= 500[kg] }
        }
    }
}
