// A package acts as a namespace for its members and a container for its owned members.
// A name with spaces or other special characters is surrounded in single quotes.
package 'Package Example' {
    // An import adds either a single imported member or all the members of an imported package to the importing package.
    public import ISQ::TorqueValue;
    private import ScalarValues::*;
    // The owned members of a package are elements directly contained in the package.
    part def Automobile;
    // A package can introduce aliases for its owned members or for individual members of other packages.
    alias Car for Automobile;
    // A qualified name is a package name (which may itself be qualified) followed by the name of one of its members, separated by ::.
    alias Torque for ISQ::TorqueValue;
}
