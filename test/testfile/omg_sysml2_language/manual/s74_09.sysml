calc def square {
    in attribute x : ScalarValues::Real;
    return :ScalarValues::Real;
    rep square language "Python"
        /*
         * def
         * square(x:float) ->
         * float:
         *     return x**2
         */
}
