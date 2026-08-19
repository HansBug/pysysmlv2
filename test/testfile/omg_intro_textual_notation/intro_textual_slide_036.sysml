action takePicture : TakePicture {
    in scene;
    out picture;
    action focus : Focus {
        in scene = takePicture::scene;
        out image;
    }
    // This is a shorthand for a conditional succession following the lexically previous action.
    if focus.image.isFocused then shoot;
    flow focus.image to shoot.image;
    action shoot : Shoot {
        in image;
        out picture;
    }
    out picture = shoot.picture;
}
