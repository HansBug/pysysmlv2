allocation a : A subsets Allocations::allocations {
    end ref e1 references f1 redefines A::e1;
    end ref e2 references f2 redefines A::e2;

    // A nested AllocationUsage is a subpart.
    allocation subsets Allocations::allocations, Items::Item::subparts
        allocate e1.x to e2.y;
}
