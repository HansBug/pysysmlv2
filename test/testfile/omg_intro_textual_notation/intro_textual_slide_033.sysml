action def Focus{ in scene : Scene; out image : Image; }
action def Shoot{ in image : Image; out picture : Picture; }

action def TakePicture {
    in scene : Scene;
    action focus : Focus {
        // This qualified name refers to the scene parameter of TakePicture, rather than the parameter of focus with the same name.
        in scene = TakePicture::scene;
        out image;
    }
    flow focus.image to shoot.image;
    // This is a shorthand for a succession between the lexically previous action (focus) and this action (shoot).
    then action shoot : Shoot {
        in image;
        out picture;
    }
    // This is the same shorthand for binding used previously.
    out picture : Picture = shoot.picture;
}
