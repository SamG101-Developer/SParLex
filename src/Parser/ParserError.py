from ordered_set import OrderedSet


class ParserError(Exception):
    """
    The ParserError class is an exception that is raised when the parser encounters an error. It contains the position
    of the error and the expected tokens at that position. The expected tokens are stored in an OrderedSet, which is a
    set that maintains the order of insertion. The expected tokens are used by the error formatter to display the error
    message.
    """

    pos: int
    expected_tokens: OrderedSet[str]

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.pos = -1
        self.expected_tokens = OrderedSet()
