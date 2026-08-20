standard library package StandardViewDefinitions {
    view def <gv> GeneralView;
    view def <iv> InterconnectionView;
    view def <afv> ActionFlowView specializes InterconnectionView;
    view def <stv> StateTransitionView specializes InterconnectionView;
    view def <sv> SequenceView;
    view def <gev> GeometryView;
    view def <gv> GridView;
    view def <bv> BrowserView;
}
