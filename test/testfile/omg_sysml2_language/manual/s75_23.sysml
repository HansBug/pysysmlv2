package PackageApprovals {
    private import ApprovalMetadata::*;
    private import SysML::*;

    // This imports all part definitions from the DesignModel that have
    // at least one owned part usage and have been marked as approved.
    public import DesignModel::**[@PartDefinition and
                                  @PartDefinition::ownedPart != null and
                                  @Approval and
                                  Approval::approved];
}
