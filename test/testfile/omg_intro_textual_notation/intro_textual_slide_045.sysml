action takePicture : TakePicture {
    // An accept action receives an incoming asynchronous transfer any kind of values.
    // This is the name of the action.
    // This is a declaration of what is being received, which can be anything.
    action trigger accept scene : Scene;
    then action focus : Focus {
        in scene = trigger.scene;
        out image;
    }
    flow from focus.image to shoot.image;
    then action shoot : Shoot {
        in image;
        out picture;
    }
    // This is an expression that constructs the value to be sent.
    // A send action is an outgoing transfer of values to a specific target.
    // The notation “Show(...)” means to create an instance of the definition Show with the given value for its nested attribute.
    // This is also an expression, evaluating to the target (in this case just a feature reference).
    then send new Show(shoot.picture) to screen;
}
