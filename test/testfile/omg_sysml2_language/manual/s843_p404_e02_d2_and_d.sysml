attribute def D2 specializes Base::DataValue {
    ref attribute a : ScalarValue::String subsets Base::dataValues;
}
ref attribute d : D2 subsets Base::dataValues {
    ref attribute b subsets a;
}
