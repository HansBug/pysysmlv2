package UpperLevelApprovals {
    // Recursively import all annotation data types and all
    // features of those types.
    private import ApprovalMetadata::**;

    // The filter condition for this import applies only to
    // elements imported from the DesignModel package.
    public import DesignModel::**[@Approval and approved and level > 1];
}
