part def Axle {
    attribute mass :> ISQ::mass;
}
part def FrontAxle :> Axle {
    attribute steeringAngle :> ISQ::angularMeasure;
}
