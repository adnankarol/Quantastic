class QuantasticError(Exception):
    """
    Base class for all Quantastic-specific exceptions.
    """

    pass


class ConfigError(QuantasticError):
    """
    Raised when there is an issue with the configuration.
    """

    pass


class DataFetchError(QuantasticError):
    """
    Raised when there is an issue fetching data.
    """

    pass
