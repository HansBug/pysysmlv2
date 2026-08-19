// A requirement definition is a special kind of constraint definition.
requirement def MassLimitationRequirement {
    // A textual statement of the requirement can be given as a documentation comment in the requirement definition body.
    doc /* The actual mass shall be less than or equal
    * to the required mass. */
    // Like a constraint definition, a requirement definition can be parameterized using features.
    attribute massActual : MassValue;
    attribute massReqd : MassValue;
    // The requirement can be formalized by giving one or more component required constraints.
    require constraint { massActual <= massReqd }
}
