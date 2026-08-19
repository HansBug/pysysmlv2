action def TakePicture {
  action focus : Focus {
    out image : Image;
  }
  action shoot : Shoot {
    in image : Image;
  }
  // The use of a succession flow usage means that focus must
  // complete before the image is transferred, after which shoot can begin.
  succession flow focus.image to shoot.image;
}
