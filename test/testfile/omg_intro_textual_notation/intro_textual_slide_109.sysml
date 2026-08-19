// The AnalysisTooling package is part of the Analysis domain library.
standard library package AnalysisTooling {
    private import ScalarValues::*;
    metadata def ToolExecution {
        attribute toolName : String;
        attribute uri : String;
    }
    metadata def ToolVariable {
        attribute name : String;
    }
}
action computeDynamics {
    private import AnalysisTooling::*;
    metadata ToolExecution {
        toolName = "ModelCenter";
        uri = "aserv://localhost/Vehicle/Equation1";
    }
    in dt : ISQ::TimeValue  {@ToolVariable {name = "deltaT";}}
    in a : ISQ:: AccelerationValue  {@ToolVariable {name = "mass";}}
    in v_in : ISQ:: VelocityValue   {@ToolVariable {name = "v0";}}
    in x_in : ISQ:: LengthValue {@ToolVariable {name = "x0";}}
    out v_out : ISQ:: VelocityValue {@ToolVariable {name = "v";}}
    out x_out : ISQ:: LengthValue   {@ToolVariable {name = "x";}}
}
