part def 'Systems Engineer';
part def 'IV&V';
// A concern is a specific topic that one or more stakeholders desire to be addressed.
concern 'system breakdown' {
    doc /*
    * To ensure that a system covers all its required capabilities,
    * it is necessary to understand how it is broken down into
    * subsystems and components that provide those capabilities.
    */
    subject system;
    // A stakeholder is a person, organization or other entity with concerns to be addressed.
    stakeholder se: 'systems engineer';
    stakeholder ivv: 'IV&V';
}
concern modularity {
    doc /*
    * There should be well defined interfaces between the parts of
    * a system that allow each part to be understood individually,
    * as well as being part of the whole system.
    */
    subject system;
    stakeholder 'systems engineer';
}
