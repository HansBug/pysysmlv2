abstract part def PartDef1 :> PartDef0;

package P {
    alias PartDefAlias1
        for PartDef1;
}
package Q {
    alias PartDefAlias2
        for PartDef1;
}
