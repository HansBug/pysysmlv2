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
    // A dependency is a relationship that indicates that one or more client elements require one or more supplier elements for their complete specification. A dependency is entirely a model-level relationship, without instance-level semantics.
    dependency from 'System Assembly'::'Computer Subsystem' to 'Software Design';
    dependency Schemata
        from 'System Assembly'::'Storage Subsystem'
        to 'Software Design'::MessageSchema, 'Software Design'::DataSchema;
}
