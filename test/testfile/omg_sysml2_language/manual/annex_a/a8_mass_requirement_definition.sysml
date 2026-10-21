requirement def MassRequirement {
    doc /*The actual mass shall be less than the required mass*/
    attribute massRequired :> ISQ::mass;
    attribute massActual :> ISQ::mass;
    require constraint { massActual <= massRequired }
}
