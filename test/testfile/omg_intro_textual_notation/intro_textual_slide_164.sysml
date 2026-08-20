standard library package Quantities {
    // A tensor quantity value represents the value of the most general kind of quantity, a tensor.
    // The numeric value of the tensor is given as an array of numbers.
    abstract attribute def TensorQuantityValue :> Collections::Array {
        attribute num : ScalarValues::Number[1..*] ordered nonunique :>> elements;
        // The value of a tensor quantity is relative to a multi-dimensional tensor measurement reference.
        attribute mRef : UnitsAndScales::TensorMeasurementReference;
        attribute :>> dimensions = mRef::dimensions;
        ...
    }
    // A vector is a tensor with a single dimension.
    abstract attribute def VectorQuantityValue :> TensorQuantityValue {
        attribute :>> mRef : UnitsAndScales::VectorMeasurementReference;
    }
    // A scalar is a vector with a single element. Its measurement reference may be a measurement unit if the scale is a ratio scale.
    abstract attribute def ScalarQuantityValue :> VectorQuantityValue {
        attribute :>> mRef : UnitsAndScales::ScalarMeasurementReference;
    }
    abstract attribute tensorQuantities: TensorQuantityValue[*] nonunique;
    abstract attribute vectorQuantities: VectorQuantityValue[*] nonunique :> tensorQuantities;
    abstract attribute scalarQuantities: ScalarQuantityValue[*] nonunique :> vectorQuantities;
    alias TensorQuantityValue as QuantityValue;
    // A quantity is a usage of a quantity value to represent a feature of something.
    alias tensorQuantities as quantity;
    ...
}
