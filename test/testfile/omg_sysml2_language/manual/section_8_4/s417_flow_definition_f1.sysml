flow def F1 specializes Flows::Message {
    item i : I redefines Flows::Message::payload;
    end p : P redefines Flows::Message::source;
    end q : Q redefines Flows::Message::target;
}
