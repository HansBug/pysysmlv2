package 'Package Example' {
    // All members from a public import are visible (re-exported) from the importing package. Members from a private import are not.
    // Visibility must be shown explicitly on import declarations. Use private visibility unless re-export is required.
    public import ISQ::TorqueValue;
    private import ScalarValues::*;
    // A private member is not visible outside the package (but it is visible to subpackages).
    private part def Automobile;
    // Members are public by default but can also be marked public explicitly.
    public alias Car for Automobile;
    alias Torque for ISQ::TorqueValue;
}
