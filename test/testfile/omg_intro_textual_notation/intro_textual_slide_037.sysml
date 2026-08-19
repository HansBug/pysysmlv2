action takePicture : TakePicture {
    // References the start of the action as the source of the initial succession.
    first start;
    // A merge node waits for exactly one predecessor to happen before continuing.
    then merge continue;
    then action trigger { out item scene; }
    flow trigger.scene to focus.scene;
    then action focus : Focus {
        in scene;
        out image;
    }
    flow focus.image to shoot.image;
    then action shoot : Shoot {
        in image;
        out picture;
    }
    flow shoot.picture to display.picture;
    then action display {
        in picture;
    }
    // References the merge node named “continue” as the target of the succession.
    then continue;
}
