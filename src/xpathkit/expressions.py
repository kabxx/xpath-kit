from typing import Any, Callable, List, Optional, Tuple, Union, override

from .exceptions import XPathEvaluationError
from .utils import xpath_str


class _node:
    """Abstract base node for XPath expression building."""

    def __str__(
        self,
    ):
        """Return the full XPath string representation of the node."""
        raise NotImplementedError

    def part(
        self,
    ) -> str:
        """Return the partial XPath string for this node."""
        raise NotImplementedError

    def full(
        self,
    ) -> str:
        """Return the full XPath string for this node."""
        raise NotImplementedError

    def __str__(self):
        """Return the full XPath string representation of the node."""
        return self.full()


class _pred(_node):
    """Predicate node for XPath expression building."""

    def __init__(
        self,
    ):
        """Initialize a predicate node for XPath expression building."""
        self._others: List[Tuple[str, _pred]] = []

    def __and__(
        self,
        value: "_pred",
    ) -> "attr":
        """Combine this predicate with another using logical AND."""
        self._others.append(
            (
                "and",
                value,
            ),
        )
        return self

    def __or__(
        self,
        value: "_pred",
    ) -> "attr":
        """Combine this predicate with another using logical OR."""
        self._others.append(
            (
                "or",
                value,
            )
        )
        return self

    @override
    def full(
        self,
    ) -> str:
        """Return the full predicate string, including all combined predicates."""
        ret = self.part()
        for conn, pred in self._others:
            ret = f"({ret} {conn} {pred.full()})"
        return ret

    @staticmethod
    def _and_join(
        *ss: str,
    ) -> str:
        """Join multiple strings with 'and' for XPath expressions."""
        ss = [s for s in ss if s is not None]
        s = " and ".join(ss)
        return f"({s})"

    @staticmethod
    def _or_join(
        *ss: str,
    ) -> str:
        """Join multiple strings with 'or' for XPath expressions."""
        ss = [s for s in ss if s is not None]
        s = " or ".join(ss)
        return f"({s})"


class expr(_pred):
    """Expression node for XPath building (supports ==, !=, >, <, etc)."""

    def __init__(
        self,
        base: Any,
    ):
        """Initialize an expression node for XPath building."""
        super().__init__()
        self._exprs = []
        self._add(None, base)

    def _add(
        self,
        op: str,
        value: Any,
    ) -> "expr":
        """Add an operation and value to the expression chain."""
        self._exprs.append((op, xpath_str(value)))
        return self

    def __eq__(
        self,
        value: Any,
    ) -> "expr":
        return self._add("=", value)

    def __ne__(
        self,
        value: Any,
    ) -> "expr":
        return self._add("!=", value)

    def __gt__(
        self,
        value: Any,
    ) -> "expr":
        return self._add(">", value)

    def __lt__(
        self,
        value: Any,
    ) -> "expr":
        return self._add("<", value)

    def __ge__(
        self,
        value: Any,
    ) -> "expr":
        return self._add(">=", value)

    def __le__(
        self,
        value: Any,
    ) -> "expr":
        return self._add(">=", value)

    def __le__(
        self,
        value: Any,
    ) -> "expr":
        return self._add("<=", value)

    @override
    def part(
        self,
    ) -> str:
        ret = ""
        for conn, expr in self._exprs:
            if ret:
                ret = f"({ret}{conn}{expr})"
            else:
                ret = expr
        return ret


class value(_pred):
    """Value node for XPath building."""

    def __init__(
        self,
        value: Any,
    ):
        """Initialize a value node for XPath building."""
        super().__init__()
        self._value = value

    @override
    def part(
        self,
    ) -> str:
        return xpath_str(self._value)


class attr(_pred):
    """Attribute predicate node for XPath building."""

    def __init__(
        self,
        name: str,
    ):
        """Initialize an attribute predicate node for XPath building."""
        super().__init__()
        self._name = name
        self._conds: List[Tuple[str, str]] = []

    def eq(
        self,
        value: Any,
    ) -> "attr":
        """Add an equality condition for the attribute."""
        self._conds.append(
            (
                "and",
                f'@{self._name}="{xpath_str(value)}"',
            )
        )
        return self

    def __eq__(
        self,
        value: Any,
    ) -> "attr":
        return self.eq(value)

    def all(
        self,
        *values: Any,
    ) -> "attr":
        """Add a condition that all values must be contained in the attribute."""
        self._conds.append(
            (
                "and",
                self._and_join(
                    *[f'contains(@{self._name},"{xpath_str(v)}")' for v in values],
                ),
            )
        )
        return self

    def any(
        self,
        *values: Any,
    ) -> "attr":
        """Add a condition that any value must be contained in the attribute."""
        self._conds.append(
            (
                "and",
                self._or_join(
                    *[f'contains(@{self._name},"{xpath_str(v)}")' for v in values],
                ),
            )
        )
        return self

    def none(
        self,
        *values: Any,
    ) -> "attr":
        """Add a condition that none of the values are contained in the attribute."""
        self._conds.append(
            (
                "and",
                self._and_join(
                    *[f'not(contains(@{self._name},"{xpath_str(v)}"))' for v in values],
                ),
            )
        )
        return self

    def or_(
        self,
        expr: Callable[["attr"], "attr"],
    ) -> "attr":
        """Combine this attribute predicate with another using logical OR."""
        return self | expr(attr(self._name))

    def and_(
        self,
        expr: Callable[["attr"], "attr"],
    ) -> "attr":
        """Combine this attribute predicate with another using logical AND."""
        return self & expr(attr(self._name))

    @override
    def part(
        self,
    ) -> str:
        if not self._conds:
            return f"@{self._name}"
        ret = ""
        for conn, val in self._conds:
            if not ret:
                ret = val
            else:
                ret = f"({ret} {conn} {val})"
        return ret


class el(_node):
    """Element node for XPath building."""

    def __init__(
        self,
        name: str,
        axis: Optional[str] = None,
    ):
        """Initialize an element node for XPath building."""
        self._name = name
        self._axis = axis
        self._preds: List[_pred] = []
        self._others: List[Tuple[str, _node]] = []

    def __getitem__(
        self,
        pred: Union["attr", "value", "expr", Any],
    ) -> "el":
        """Add a predicate to this element node."""
        if not isinstance(pred, _pred):
            pred = value(pred)
        self._preds.append(pred)
        return self

    def __truediv__(
        self,
        value: Union[str, "el"],
    ) -> "el":
        """Add a direct child element to this element node."""
        if isinstance(value, str):
            value = el(value)
        elif isinstance(value, el):
            value = value
        else:
            raise XPathEvaluationError("connected value must be a element or string")
        self._others.append(
            (
                "/",
                value,
            )
        )
        return self

    def __floordiv__(
        self,
        value: Union[str, "el"],
    ) -> "el":
        """Add a descendant element to this element node."""
        if isinstance(value, str):
            value = el(value)
        elif isinstance(value, el):
            value = value
        else:
            raise XPathEvaluationError("connected value must be a element or string")
        self._others.append(
            (
                "//",
                value,
            )
        )
        return self

    @override
    def part(
        self,
    ) -> str:
        ret = self._name
        if self._axis is not None:
            ret = f"{self._axis}::{ret}"
        for pred in self._preds:
            ret = f"{ret}[{pred.full()}]"
        return ret

    @override
    def full(
        self,
    ) -> str:
        ret = self.part()
        for conn, other in self._others:
            ret += f"{conn}{other.full()}"
        return ret
