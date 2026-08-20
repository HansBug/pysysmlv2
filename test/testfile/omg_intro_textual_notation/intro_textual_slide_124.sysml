standard library package VectorValues {
    private import ScalarValues::NumericalValue;
    private import ScalarValues::Real;
    private import Collections::Array;
    abstract datatype VectorValue;
    datatype NumericalVectorValue :> VectorValue, Array {
        feature dimension[0..1] :>> dimensions;
        feature :>> elements : NumericalValue;
    }
    datatype CartesianVectorValue :> NumericalVectorValue {
        feature :>> elements : Real;
    }
    datatype ThreeVectorValue :> NumericalVectorValue {
        feature :>> dimension = 3;
    }
    datatype CartesianThreeVectorValue :> CartesianVectorValue, ThreeVectorValue;
}
