from typing import Any, Callable, List, Optional, Tuple, Union, override

from .exceptions import XPathEvaluationError


class expr:
    """Abstract base node for XPath expression building."""

    def __init__(
        self,
        **kwargs: Any,
    ):
        """Initialize an expression node for XPath expressions."""
        super().__init__(**kwargs)

    def __str__(self):
        """Return the full XPath string representation of the node."""
        return self.compile()

    def _compile_self(
        self,
    ) -> str:
        """Return the partial XPath string for this node."""
        raise NotImplementedError

    def compile(
        self,
    ) -> str:
        """Return the full XPath string for this node."""
        raise NotImplementedError

    @staticmethod
    def _any_to_str_in_expr(
        val: Any,
    ) -> str:
        """Convert any value to a string representation in the context of XPath expressions."""
        if isinstance(val, str):
            return f'"{val}"'
        elif isinstance(val, expr):
            return val.compile()
        else:
            return _any_to_xpath_str(val)


class _atom(expr):
    """Base class for atomic XPath expression nodes."""

    def __init__(
        self,
        **kwargs: Any,
    ):
        """Initialize an atomic node for XPath expressions."""
        super().__init__(**kwargs)

    def _compile_self(
        self,
    ) -> str:
        raise NotImplementedError

    def compile(
        self,
    ) -> str:
        return self._compile_self()


class _any(_atom):
    """Atomic node for any value in XPath expressions (used for constants, numbers, booleans, etc.)."""

    def __init__(
        self,
        value: Any,
        **kwargs: Any,
    ):
        """Initialize an atomic node for XPath expressions."""
        self._value = value
        super().__init__(**kwargs)

    @override
    def _compile_self(
        self,
    ) -> str:
        return _any_to_xpath_str(self._value)


class _str(_atom):
    """Atomic node for string values in XPath expressions."""

    def __init__(
        self,
        value: str,
        **kwargs: Any,
    ):
        """Initialize a string node for XPath expressions."""
        self._value = value
        super().__init__(**kwargs)

    @override
    def _compile_self(
        self,
    ) -> str:
        return self._value


class _index(_atom):
    """Atomic node for index values in XPath expressions (handles negative and positive indices)."""

    def __init__(
        self,
        value: int,
        **kwargs: Any,
    ):
        """Initialize an index node for XPath expressions."""
        self._value = value
        super().__init__(**kwargs)

    @override
    def _compile_self(
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
    """A boolean expression for XPath predicates."""

    def __init__(
        self,
        **kwargs: Any,
    ):
        """Initialize a boolean expression for XPath predicates."""
        self._others: List[Tuple[str, _bool]] = []
        super().__init__(**kwargs)

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
    def compile(
        self,
    ) -> str:
        ret = self._compile_self()
        for conn, other in self._others:
            ret = f"({ret} {conn} {other.compile()})"
        return ret


class _cond(_bool):
    """A conditional expression for XPath predicates."""

    def __init__(
        self,
        key: str,
        **kwargs: Any,
    ):
        """Initialize a conditional expression for XPath predicates."""
        self._key = key
        self._conds: List[Tuple[str, str]] = []
        super().__init__(**kwargs)

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
        """Match all values in the list."""
        return self._add_cond(
            self._and_join(
                *[f"contains({self._key},{expr._any_to_str_in_expr(v)})" for v in values],
            ),
        )

    def any(
        self,
        *values: Any,
    ) -> "_cond":
        """Match any value in the list."""
        return self._add_cond(
            self._or_join(
                *[f"contains({self._key},{expr._any_to_str_in_expr(v)})" for v in values],
            ),
        )

    def none(
        self,
        *values: Any,
    ) -> "_cond":
        """Match no values in the list."""
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
    def _compile_self(
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
    def compile(
        self,
    ) -> str:
        """Return the full predicate string, including all combined predicates."""
        ret = self._compile_self()
        for conn, other in self._others:
            ret = f"({ret} {conn} {other.compile()})"
        return ret

    @staticmethod
    def _any_to_str_in_cond(
        arg: Union["_cond", Any],
    ) -> str:
        """Convert any value to a string representation in the context of predicates."""
        if isinstance(arg, str):
            return f'"{arg}"'
        elif isinstance(arg, _cond):
            return arg.compile()
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
        **kwargs: Any,
    ):
        """Initialize an attribute predicate node for XPath building."""
        self._name = name
        super().__init__(
            key=f"@{self._name}",
            **kwargs,
        )

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


class fun(_cond):
    """Function node for XPath expressions, e.g. fun('text')."""

    def __init__(
        self,
        name: str,
        *args: Union["fun", "attr", "dot", Any],
        **kwargs: Any,
    ):
        """Initialize a function node for XPath expressions."""
        super().__init__(
            key=f"{name}({','.join(expr._any_to_str_in_expr(arg) for arg in args)})",
            **kwargs,
        )


class dot(_cond):
    """Node representing the current context (dot) in XPath expressions."""

    def __init__(
        self,
        **kwargs: Any,
    ):
        """Initialize a dot node representing the current context in XPath."""
        super().__init__(
            key=f".",
            **kwargs,
        )


class ele(expr):
    """Element node for building XPath expressions."""

    def __init__(
        self,
        name: str,
        axis: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize an element node for XPath building."""
        self._name = name
        self._axis = axis
        self._exprs: List[expr] = []
        self._others: List[Tuple[str, "ele"]] = []
        super().__init__(**kwargs)

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
        return self._add_expr(_any_to_expr_in_pred(pred))

    def __truediv__(
        self,
        other: Union[str, expr],
    ) -> "ele":
        """Add a direct child element to this element node."""
        if isinstance(other, dot):
            raise XPathEvaluationError("dot() is not allowed as a descendant element. Because it represents the current context node.")
        return self._add_other(
            conn="/",
            other=ele._any_to_expr_in_ele(other),
        )

    def __floordiv__(
        self,
        other: Union[str, expr],
    ) -> "ele":
        """Add a descendant element to this element node."""
        if isinstance(other, dot):
            raise XPathEvaluationError("dot() is not allowed as a descendant element. Because it represents the current context node.")
        return self._add_other(
            conn="//",
            other=ele._any_to_expr_in_ele(other),
        )

    @override
    def _compile_self(
        self,
    ) -> str:
        ret = self._name
        if self._axis is not None:
            ret = f"{self._axis}::{ret}"
        for expr in self._exprs:
            ret = f"{ret}[{expr.compile()}]"
        return ret

    @override
    def compile(
        self,
    ) -> str:
        ret = self._compile_self()
        for conn, other in self._others:
            ret += f"{conn}{other.compile()}"
        return ret

    @staticmethod
    def _any_to_expr_in_ele(
        val: Any,
    ) -> expr:
        """Convert any value to a xpath expression in element context."""
        if isinstance(val, ele):
            return val
        elif isinstance(val, str):
            return ele(val)
        elif isinstance(val, expr):
            return val
        else:
            raise XPathEvaluationError("Value must be a string or expr.")


def _any_to_expr_in_pred(
    val: Any,
) -> expr:
    """Convert any value to a xpath expression in predicates."""
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
    """
    Convert any value to its string representation for XPath.
    Booleans are converted to 'true'/'false', others use str().
    """
    if isinstance(val, bool):
        return str(val).lower()
    return str(val)
