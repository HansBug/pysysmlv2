// Implicitly specializes Connections::BinaryConnection by default.
connection def AssetOwnership {
  attribute valuationOnPurchase : MonetaryValue;
  end [1..*] item owner : LegalEntity; // Implicitly redefines BinaryConnection::source.
  end [*] item ownedAsset : Asset; // Implicitly redefines BinaryConnection::target.
}
connection def SoleOwnership specializes AssetOwnership {
  end [1] item owner; // Implicitly redefines Ownership::owner.
  // ownedAsset is inherited.
}
