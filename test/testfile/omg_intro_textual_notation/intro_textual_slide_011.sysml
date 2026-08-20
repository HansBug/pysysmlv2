part def Vehicle {
    part parts : VehiclePart[*];
    // Subsetting asserts that, in any common context, the values of one feature are a subset of the values of another feature.
    // Subsetting is a kind of generalization between features.
    part eng : Engine subsets parts;
    part trans : Transmission subsets parts;
    part wheels : Wheel[4] :> parts;
}
abstract part def VehiclePart;
part def Engine :> VehiclePart;
part def Transmission :> VehiclePart;
part def Wheel :> VehiclePart;
