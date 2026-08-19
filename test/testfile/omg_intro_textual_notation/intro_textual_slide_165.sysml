standard library package MeasurementReferences {
    // A tensor measurement reference is defined as an array of scalar measurement references, one for each element of the tensor.
    attribute def TensorMeasurementReference :> Array {
        attribute mRefs : ScalarMeasurementReference[1..*] :>> elements;
        ...
    }
    attribute def VectorMeasurementReference
    :> TensorMeasurementReference {
        attribute :>> dimensions: Positive[0..1];
        ...
    }
    attribute def ScalarMeasurementReference
    :> VectorMeasurementReference {
        attribute :>> dimensions = ();
        ...
    }
    // A coordinate frame is a kind of vector measurement reference that can be located and oriented relative to another frame using a coordinate transformation.
    attribute def CoordinateFrame :> VectorMeasurementReference {
        attribute transformation: CoordinateTransformation[0..1];
    }
    ...
}
