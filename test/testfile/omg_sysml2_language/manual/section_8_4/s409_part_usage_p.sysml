part def P specializes Parts::Part {
    ref part a subsets Parts::parts;
    part b subsets Items::Item::subparts;
    item c subsets Items::Item::subitems {
        part p : P subsets Items::Item::subparts;
    }
}
