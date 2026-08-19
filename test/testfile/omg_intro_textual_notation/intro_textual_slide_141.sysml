standard library package VectorFunctions {
    ...
    function CartesianVectorOf
    {in components: NumericalValue[1..*] ordered nonunique; return : CartesianVectorValue[1];}
    function CartesianThreeVectorOf specializes CartesianVectorOf
    {in components: Real[3] ordered nonunique; return : CartesianVectorValue[1];}
    function isCartesianZeroVector specializes isZeroVector
    {in v: CartesianVectorValue[1]; return : Boolean[1];}
    function 'cartesian+' specializes '+'
    {in v: CartesianVectorValue[1]; in w: CartesianVectorValue[0..1]; return: CartesianVectorValue[1];
        function 'cartesian-' specializes '-'
        {in v: CartesianVectorValue[1]; in w: CartesianVectorValue[0..1]; return: CartesianVectorValue[1];
            function cartesianScalarVectorMult specializes scalarVectorMult
            {in x: Real[1]; in v: CartesianVectorValue[1]; return : CartesianVectorValue[1];}
            function cartesianVectorScalarMult specializes vectorScalarMult
            {in v: CartesianVectorValue[1]; in x: Real[1]; return : CartesianVectorValue[1];}
            function cartesianInner specializes inner
            {in v: CartesianVectorValue[1]; in w: CartesianVectorValue[0..1]; return : Real[1];}
            function cartesianNorm specializes norm
            {in v: CartesianVectorValue[1]; return : NumericalValue[1];}
            function cartesianAngle specializes angle
            {in v: CartesianVectorValue[1]; in w: CartesianVectorValue[0..1]; return : Real[1];}
            function sum {in coll: CartesianThreeVectorValue[*]; return : CartesianThreeVectorValue[0..1];}
        }
