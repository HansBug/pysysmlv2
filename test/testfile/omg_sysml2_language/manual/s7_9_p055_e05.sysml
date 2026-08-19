part client {
    event occurrence request[1] references subscriptionMessage.source;
    event occurrence delivery[*] ::> publicationMessage.target;
}
