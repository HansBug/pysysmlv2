interface def WaterDelivery {
    // Connection ends specify the participants in the connection. They always have multiplicity 1..1 relative to the connection definition.
    end [1] port suppliedBy : SpigotBank {
        port hot : Spigot;
        port cold : Spigot;
    }
    // Every suppliedBy SpigotBank must have one or more connections to deliveredTo Faucets.
    // Cross multiplicities correspond to navigating across connections.
    end [1..*] port deliveredTo : Faucet {
        port hot : FaucetInlet;
        port cold : FaucetInlet;
    }
    // Connection usages interconnect specific participants.
    connect suppliedBy.hot to deliveredTo.hot;
    connect suppliedBy.cold to deliveredTo.cold;
}
