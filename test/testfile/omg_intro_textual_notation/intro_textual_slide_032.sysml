action def Focus{ in scene : Scene; out image : Image; }
action def Shoot{ in image : Image; out picture : Picture; }
action def TakePicture {
    in scene : Scene;
    out picture : Picture;
    bind focus.scene = scene;
    action focus : Focus { in scene; out image; }
    // A succession flow requires the first action to finish producing its output before the second can begin consuming it.
    succession flow focus.image to shoot.image;
    action shoot : Shoot { in image; out picture; }
    bind shoot.picture = picture;
}
