// A textual representation annotation can actually be used with any kind of element, not just actions. OMG-standard languages a tool may support include "OCL" (Object Constraint Language) and "Alf" (Action Language for fUML). A tool can also provide support for other languages (e.g., "JavaScript" or "Modelica").
action def UpdateSensors {
    in sensors : Sensor[*];
    // An "opaque" action definition or usage can be specified using a textual representation annotation in a language other than SysML.
    language "Alf"
    // The textual representation body is written using comment syntax. The /*, */ and leading * symbols are not included in the body text. Note that support for referencing SysML elements from the body text is tool-specific.
    /*
    * for (sensor in sensors) {
    *     if (sensor.ready) {
    *         Update(sensor);
    *     }
    * }
    */
}
