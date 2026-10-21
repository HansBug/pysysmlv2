connection def C specializes Connections::Connection {
    end ref e1 subsets Links::Link::participant;
    end ref e2 subsets Links::Link::participant;
    end ref e3 subsets Links::Link::participant;
}
connection def D specializes C {
    end ref f1 redefines C::e1;
    end ref f2 redefines C::e2;
    end ref f3 redefines C::e3;
}
