standard library package ImageMetadata {
    private import ScalarValues::String;
    // Provides data necessary for the physical definition of a graphical image.
    attribute def Image {
        // Binary data for the image.
        attribute content : String[0..1];
        // Binary data character encoding (e.g., "base64").
        attribute encoding : String[0..1];
        // MIME type of the content.
        attribute type : String[0..1];
        // URI for image content, alternative to embedding it in the content attribute.
        attribute location : String[0..1];
    }
    // To be used to annotate a model element with an image.
    metadata def Icon {
        // Full-sized image for rendering the annotated element.
        attribute fullImage : Image[0..1];
        // Smaller image for use as an adornment or marker.
        attribute smallImage : Image[0..1];
    }
}
