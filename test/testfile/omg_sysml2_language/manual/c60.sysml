part def Vehicle {
  attribute def ControlSignal;
  part controller {
    event occurrence sendControl;
  }
  part engine {
    event occurrence receiveControl;
  }
  message of ControlSignal from controller.sendControl to engine.receiveControl;
}
