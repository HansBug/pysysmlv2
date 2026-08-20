action takePicture : TakePicture {
    in scene;
    action focus : Focus {
        in scene = takePicture::scene;
        out image;
    }
    first focus
    // A conditional succession asserts that the second action must follow the first only if a guard condition is true. If the guard is false, succession is not possible.
    // Note that, currently, the target action must be explicitly named (no shorthand).
    if focus.image.isFocused then shoot;
    flow focus.image to shoot.image;
    action shoot : Shoot {
        in image;
        out picture;
    }
    out picture = shoot.picture;
}
