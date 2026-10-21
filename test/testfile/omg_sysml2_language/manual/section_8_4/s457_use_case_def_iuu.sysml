use case def UIU specializes UseCases::UseCases {
    include use case iu1 references uc1
        subsets UseCases::UseCase::includedUseCases;
    include use case iu2 subsets UseCases::useCases
        subsets UseCases::UseCase::includedUseCases;
}
