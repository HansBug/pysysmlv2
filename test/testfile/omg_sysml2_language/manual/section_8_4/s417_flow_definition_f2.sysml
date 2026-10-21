part def P specializes Parts::Part {
    port p1 : Pd subsets Parts::Part::ownedPorts;
}
part def Q specializes Parts::Part {
    port p2 : ~Pd subsets Parts::Part::ownedPorts;
}
flow def F2 specializes Flows::Flow {
    item i : I redefines Flows::Flow::payload;
    end p : P redefines Flows::Flow::source {
        port p1 redefines P::p1, Flows::Flow::source::sourceInput;
    }
    end q : Q redefines Flows::Flow::target {
        port p2 redefines Q::p2, Flows::Flow::source::targetOuput;
    }
}
