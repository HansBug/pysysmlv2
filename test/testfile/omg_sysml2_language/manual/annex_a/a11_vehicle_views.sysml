package VehicleViews {
    view vehiclePartsTree_Safety : PartsTreeView {
        satisfy safetyViewpoint;
        filter @Safety;
        expose vehicle_b::**;
    }
}
