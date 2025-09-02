from typing import Any, Callable, List, Optional, Tuple, Union, override

from .exceptions import XPathEvaluationError


class expr:
    """Abstract base node for XPath expression building."""

    def __str__(self):
        """Return the full XPath string representation of the node."""
        return self.full()

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

    @staticmethod
    def _any_to_str_in_expr(
        val: Any,
    ) -> str:
        if isinstance(val, str):
            return f'"{val}"'
        elif isinstance(val, expr):
            return val.full()
        else:
            return _any_to_xpath_str(val)


class _atom(expr):

    def part(
        self,
    ) -> str:
        raise NotImplementedError

    def full(
        self,
    ) -> str:
        return self.part()


class _any(_atom):

    def __init__(
        self,
        value: Any,
    ):
        self._value = value
        super().__init__()

    @override
    def part(
        self,
    ) -> str:
        return _any_to_xpath_str(self._value)


class _str(_atom):

    def __init__(
        self,
        value: str,
    ):
        self._value = value
        super().__init__()

    @override
    def part(
        self,
    ) -> str:
        return self._value


class _index(_atom):

    def __init__(
        self,
        value: int,
    ):
        self._value = value
        super().__init__()

    @override
    def part(
        self,
    ) -> str:
        if self._value < 0:
            offset = abs(self._value) - 1
            return f"last()-{offset}" if offset > 0 else "last()"
        elif self._value == 0:
            raise XPathEvaluationError("Zero is not a valid XPath index")
        else:
            return str(self._value)


class _bool(expr):
    """Predicate node for XPath expression building."""

    def __init__(
        self,
    ):
        """Initialize a predicate node for XPath expression building."""
        self._others: List[Tuple[str, _bool]] = []

    def _add_other(
        self,
        conn: str,
        other: "_bool",
    ) -> "_bool":
        self._others.append(
            (
                conn,
                other,
            ),
        )
        return self

    def __and__(
        self,
        other: "_bool",
    ) -> "_bool":
        return self._add_other("and", other)

    def __or__(
        self,
        other: "_bool",
    ) -> "_bool":
        return self._add_other("or", other)

    @override
    def full(
        self,
    ) -> str:
        ret = self.part()
        for conn, other in self._others:
            ret = f"({ret} {conn} {other.full()})"
        return ret


class _cond(_bool):

    def __init__(
        self,
        key: str,
    ):
        self._key = key
        self._conds: List[Tuple[str, str]] = []
        super().__init__()

    @property
    def key(
        self,
    ) -> str:
        return self._key

    def _add_cond(
        self,
        cond: str,
    ) -> "_cond":
        self._conds.append(cond)
        return self

    def eq(
        self,
        value: Any,
    ) -> "_cond":
        return self._add_cond(f"{self._key}={expr._any_to_str_in_expr(value)}")

    def ne(
        self,
        value: Any,
    ) -> "_cond":
        return self._add_cond(f"{self._key}!={expr._any_to_str_in_expr(value)}")

    def gt(
        self,
        value: Any,
    ) -> "_cond":
        return self._add_cond(f"{self._key}>{expr._any_to_str_in_expr(value)}")

    def lt(
        self,
        value: Any,
    ) -> "_cond":
        return self._add_cond(f"{self._key}<{expr._any_to_str_in_expr(value)}")

    def ge(
        self,
        value: Any,
    ) -> "_cond":
        return self._add_cond(f"{self._key}>={expr._any_to_str_in_expr(value)}")

    def le(
        self,
        value: Any,
    ) -> "_cond":
        return self._add_cond(f"{self._key}<={expr._any_to_str_in_expr(value)}")

    def starts_with(
        self,
        value: Any,
    ) -> "_cond":
        return self._add_cond(f"starts-with({self._key},{expr._any_to_str_in_expr(value)})")

    def ends_with(
        self,
        value: Any,
    ) -> "_cond":
        return self._add_cond(f"ends-with({self._key},{expr._any_to_str_in_expr(value)})")

    def contains(
        self,
        value: Any,
    ) -> "_cond":
        return self._add_cond(f"contains({self._key},{expr._any_to_str_in_expr(value)})")

    def all(
        self,
        *values: Any,
    ) -> "_cond":
        return self._add_cond(
            self._and_join(
                *[f"contains({self._key},{expr._any_to_str_in_expr(v)})" for v in values],
            ),
        )

    def any(
        self,
        *values: Any,
    ) -> "_cond":
        return self._add_cond(
            self._or_join(
                *[f"contains({self._key},{expr._any_to_str_in_expr(v)})" for v in values],
            ),
        )

    def none(
        self,
        *values: Any,
    ) -> "_cond":
        return self._add_cond(
            self._and_join(
                *[f"not(contains({self._key},{expr._any_to_str_in_expr(v)}))" for v in values],
            ),
        )

    def __eq__(
        self,
        value: Any,
    ) -> "attr":
        return self.eq(value)

    def __ne__(
        self,
        value: Any,
    ):
        return self.ne(value)

    def __gt__(
        self,
        value: Any,
    ) -> "attr":
        return self.gt(value)

    def __lt__(
        self,
        value: Any,
    ) -> "attr":
        return self.lt(value)

    def __ge__(
        self,
        value: Any,
    ) -> "attr":
        return self.ge(value)

    def __le__(
        self,
        value: Any,
    ) -> "attr":
        return self.le(value)

    @override
    def part(
        self,
    ) -> str:
        if not self._conds:
            return f"{self._key}"
        ret = ""
        for cond in self._conds:
            if not ret:
                ret = cond
            else:
                ret = f"({ret} and {cond})"
        return ret

    @override
    def full(
        self,
    ) -> str:
        """Return the full predicate string, including all combined predicates."""
        ret = self.part()
        for conn, other in self._others:
            ret = f"({ret} {conn} {other.full()})"
        return ret

    @staticmethod
    def _any_to_str(
        arg: Union["_cond", Any],
    ) -> str:
        if isinstance(arg, str):
            return f'"{arg}"'
        elif isinstance(arg, _cond):
            return arg.full()
        else:
            return _any_to_xpath_str(arg)

    @staticmethod
    def _and_join(
        *ss: str,
    ) -> str:
        ss = [s for s in ss if s is not None]
        s = " and ".join(ss)
        return f"({s})"

    @staticmethod
    def _or_join(
        *ss: str,
    ) -> str:
        ss = [s for s in ss if s is not None]
        s = " or ".join(ss)
        return f"({s})"


class attr(_cond):
    """Attribute predicate node for XPath building."""

    def __init__(
        self,
        name: str,
    ):
        """Initialize an attribute predicate node for XPath building."""
        self._name = name
        super().__init__(key=f"@{self._name}")

    def or_(
        self,
        fun: Callable[["attr"], "attr"],
    ) -> "attr":
        """Combine this attribute predicate with same name attribute using logical OR."""
        return self | fun(attr(name=self._name))

    def and_(
        self,
        fun: Callable[["attr"], "attr"],
    ) -> "attr":
        """Combine this attribute predicate with same name attribute using logical AND."""
        return self & fun(attr(name=self._name))


class dot(_cond):
    def __init__(
        self,
    ):
        """Initialize an attribute predicate node for XPath building."""
        super().__init__(key=f".")


class fun(_cond):
    def __init__(
        self,
        name: str,
        *args: Union["fun", "attr", "dot", Any],
    ):
        super().__init__(key=f"{name}({','.join(expr._any_to_str_in_expr(arg) for arg in args)})")


class ele(expr):
    """Element node for XPath building."""

    def __init__(
        self,
        name: str,
        axis: Optional[str] = None,
    ):
        """Initialize an element node for XPath building."""
        self._name = name
        self._axis = axis
        self._exprs: List[expr] = []
        self._others: List[Tuple[str, "ele"]] = []

    def _add_expr(
        self,
        expr: expr,
    ) -> "ele":
        self._exprs.append(expr)
        return self

    def _add_other(
        self,
        conn: str,
        other: "ele",
    ) -> "ele":
        self._others.append((conn, other))
        return self

    def __getitem__(
        self,
        pred: Union[int, str, attr, dot, fun, Any],
    ) -> "ele":
        """Add a predicate to this element node."""
        return self._add_expr(_any_to_expr(pred))

    def __truediv__(
        self,
        other: Union[str, "ele"],
    ) -> "ele":
        """Add a direct child element to this element node."""
        return self._add_other(
            conn="/",
            other=ele._any_to_expr_in_ele(other),
        )

    def __floordiv__(
        self,
        other: Union[str, "ele"],
    ) -> "ele":
        """Add a descendant element to this element node."""
        return self._add_other(
            conn="//",
            other=ele._any_to_expr_in_ele(other),
        )

    @override
    def part(
        self,
    ) -> str:
        ret = self._name
        if self._axis is not None:
            ret = f"{self._axis}::{ret}"
        for expr in self._exprs:
            ret = f"{ret}[{expr.full()}]"
        return ret

    @override
    def full(
        self,
    ) -> str:
        ret = self.part()
        for conn, other in self._others:
            ret += f"{conn}{other.full()}"
        return ret

    @staticmethod
    def _any_to_expr_in_ele(
        val: Any,
    ) -> expr:
        if isinstance(val, ele):
            return val
        elif isinstance(val, str):
            return ele(val)
        elif isinstance(val, expr):
            return val
        else:
            raise XPathEvaluationError("Value must be a string or expression")


def _any_to_expr(
    val: Any,
) -> expr:
    """Convert any value to a xpath predicate."""
    if isinstance(val, expr):
        return val
    elif isinstance(val, bool):
        return _any(val)
    elif isinstance(val, int):
        return _index(val)
    elif isinstance(val, str):
        return _str(val)
    else:
        return _any(val)


def _any_to_xpath_str(
    val: Any,
) -> str:
    """Convert any value to its string representation for XPath, with booleans as 'true'/'false'."""
    if isinstance(val, bool):
        return str(val).lower()
    return str(val)
