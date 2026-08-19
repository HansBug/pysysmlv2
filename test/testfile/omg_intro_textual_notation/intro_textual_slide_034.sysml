action def Focus{ in scene : Scene; out image : Image; }
action def Shoot{ in image : Image; out picture : Picture; }
action def TakePicture{in scene : Scene; out picture : Picture;}
// An action usage can also be directly decomposed into other actions.
action takePicture : TakePicture {
    // takePicture is a usage, so dot notation could be used here, but it is unnecessary because scene is in an outer scope, not nested.
    in scene;
    action focus : Focus {
        in scene = takePicture::scene;
        out image;
    }
    flow focus.image to shoot.image;
    then action shoot : Shoot {
        in image;
        out picture;
    }
    out picture = shoot.picture;
}
