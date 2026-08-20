package 'Dependency Example' {
    part 'System Assembly' {
        part 'Computer Subsystem' {
            ...
        }
        part 'Storage Subsystem' {
            ...
        }
    }
    package 'Software Design' {
        item def MessageSchema {
            ...
        }
        item def DataSchema {
            ...
        }
    }
    // A dependency is a relationship that indicates that one or more client elements require one more supplier elements for their complete specification. A dependency is entirely a model-level relationship, without instance-level semantics.
    // A dependency can be between any kinds of elements, generally meaning that a change to a supplier may necessitate a change to the client element.
    dependency from 'System Assembly'::'Computer Subsystem' to 'Software Design';
    // A dependency can have multiple clients and/or suppliers.
    dependency Schemata
        from 'System Assembly'::'Storage Subsystem'
        to 'Software Design'::MessageSchema, 'Software Design'::DataSchema;
}
