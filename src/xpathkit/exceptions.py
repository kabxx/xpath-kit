class XPathError(Exception):
    """Base exception for all errors raised by xpathkit."""

    pass


class XPathEvaluationError(XPathError):
    """Raised when there is an error in evaluating an XPath expression, such as syntax errors or invalid operations."""

    pass


class XPathSelectionError(XPathError):
    """Raised when an XPath query does not return the expected number of elements (e.g., not exactly one, or none found)."""

    pass


class XPathModificationError(XPathError):
    """Raised when an error occurs while modifying the XML/HTML tree, such as removing a non-child element or invalid mutation."""

    pass
