part camera : Camera {
    // perform identifies the owner as the performer of an action.
    // takePhoto is the local name of the performing action.
    perform action takePhoto[*] ordered
    // The performing action references the performed action takePicture.
    references takePicture;
    part f : AutoFocus {
        // This shorthand simply identifies the performed action owned elsewhere without renaming it locally.
        perform takePhoto.focus;
    }
    part i : Imager {
        perform takePhoto.shoot;
    }
}
