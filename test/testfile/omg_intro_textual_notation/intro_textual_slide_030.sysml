// An action definition is a definition of some action to be performed.
// Directed features of an action definition are considered to be action parameters.
action def Focus{ in scene : Scene; out image : Image; }
action def Shoot{ in image : Image; out picture : Picture; }
action def TakePicture {
    in scene : Scene;
    out picture : Picture;
    bind focus.scene = scene;
    // An action is a usage of an action definition performed in a specific context.
    // An action has parameters corresponding to its action definition.
    action focus : Focus { in scene; out image; };
    // A flow can be used to transfer items between actions.
    flow focus.image to shoot.image;
    action shoot : Shoot { in image; out picture; }
    bind shoot.picture = picture;
}
