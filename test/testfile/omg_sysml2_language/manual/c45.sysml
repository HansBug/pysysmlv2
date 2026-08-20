part def DistributedSystem {
  item def Request;
  item def Response;
  part client {
    port clientPort;
    action clientBehavior {
      send new Request() via clientPort;
      then accept Response via clientPort;
    }
  }

  part server {
    port serverPort;
    action serverBehavior {
      accept Request via serverPort;
      then send new Response() via serverPort;
    }
  }

  // Transfers from the clientPort automatically target the serverPort
  // and vice versa.
  interface client.clientPort to server.serverPort;
}
