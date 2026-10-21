interface def I1 specializes Interfaces::Interface {
    end port p1 subsets Links::Link::participant;
    end port p2 subsets Links::Link::participant;
    end port p3 subsets Links::Link::participant;
}
interface def I2 specializes Interfaces::BinaryInterface {
    end port p1 redefines Interfaces::BinaryInterface::source;
    end port p2 redefines Interfaces::BinaryInterface::target;
}
