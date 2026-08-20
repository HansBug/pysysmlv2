use case useCase1 {
    subject system = system1;
    actor actor1 : Actor1;
    actor actor2 : Actor2;
    actor actor3 : Actor3;
    include useCase2;
    include useCase3;
}
use case useCase2;
use case useCase3;
