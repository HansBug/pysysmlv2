action def Focus{ in scene : Scene; out image : Image; }
action def Shoot{ in image : Image; out picture : Picture; }
action def TakePicture {
    in scene : Scene;
    out picture : Picture;
    bind focus.scene = scene;
    action focus : Focus { in scene; out image; }
    flow focus.image to shoot.image;
    // A succession asserts that the first action must complete before the second can begin.
    first focus then shoot;
    action shoot : Shoot { in image; out picture; }
    bind shoot.picture = picture;
}
