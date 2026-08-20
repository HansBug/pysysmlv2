package Configurations {
    attribute def ConfigEntry {
        attribute key: String;
        attribute value: String;
    }
    item ConfigData {
        attribute entries[*]: ConfigEntry;
    }
}
