standard library package SampledFunctions {
    ...
    // SamplePair is a key-value pair of a domain-value and a range-value, used as a sample element in SampledFunction.
    attribute def SamplePair :> KeyValuePair {
        attribute domainValue :>> key;
        attribute rangeValue :>> val;
    }
    // SampleFunction is a variable-size, ordered collection of SamplePair elements representing a discretely sampled mathematical function.
    attribute def SampledFunction :> OrderedMap {
        attribute samples: SamplePair[0..*] ordered :>> elements;
        // The function is constrained to be strictly increasing or strictly decreasing.
        assert constraint { ... }
    }
    // Domain and Range return all the domain values and range values of a sampled function.
    calc def Domain{in fn : SampledFunction;
        return : Anything[0..*] = fn.samples.domainValue;}
    calc def Range{in fn : SampledFunction;
        return : Anything[0..*] = fn.samples.rangeValue;}
    // Sample a calculation on given domain values to create a SampledFunction.
    calc def Sample {in calc calculation {in x;}
        in attribute domainValues [0..*];
        return sampling;
        // Interpolate a SampledFunction to compute a result for a given domain value.
        calc def Interpolate {in attribute fn : SampledFunction;
            in attribute value;
            return attribute result;}
        calc interpolateLinear : Interpolate { ... }
    }
