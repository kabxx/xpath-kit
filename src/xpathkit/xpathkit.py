"""
xpathkit.py
Extension toolkit for lxml.etree XPath operations.
Author: Kabxx
License: MIT
"""

from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union, override

import lxml
import lxml.etree


def _to_str(value: Any) -> str:
    """Convert a value to its string representation for XPath, with booleans as 'true'/'false'."""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


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
        self._exprs.append((op, _to_str(value)))
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
        return _to_str(self._value)


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
                f'@{self._name}="{_to_str(value)}"',
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
                    *[f'contains(@{self._name},"{_to_str(v)}")' for v in values],
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
                    *[f'contains(@{self._name},"{_to_str(v)}")' for v in values],
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
                    *[f'not(contains(@{self._name},"{_to_str(v)}"))' for v in values],
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


class ele(_node):
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
    ) -> "ele":
        """Add a predicate to this element node."""
        if not isinstance(pred, _pred):
            pred = value(pred)
        self._preds.append(pred)
        return self

    def __truediv__(
        self,
        value: Union[str, "ele"],
    ) -> "ele":
        """Add a direct child element to this element node."""
        if isinstance(value, str):
            value = ele(value)
        elif isinstance(value, ele):
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
        value: Union[str, "ele"],
    ) -> "ele":
        """Add a descendant element to this element node."""
        if isinstance(value, str):
            value = ele(value)
        elif isinstance(value, ele):
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


class XPathElement:
    """
    A wrapper for lxml.etree._Element, providing convenient XPath and DOM-like operations.
    """

    def __init__(
        self,
        element: lxml.etree._Element,
    ):
        """Initialize a XPathElement with a lxml.etree._Element."""
        self._ele = element

    @staticmethod
    def create(
        tag: str,
        attr: Optional[Dict[str, str]] = None,
        text: Optional[str] = None,
    ) -> "XPathElement":
        element = lxml.etree.Element(tag, attrib=attr or {})
        element.text = text
        return XPathElement(element)

    @property
    def tag(self) -> str:
        """Return the tag name of the element."""
        return self._ele.tag

    @property
    def attr(self) -> Dict[str, str]:
        """Return the attribute dictionary of the element."""
        return self._ele.attrib

    @property
    def start(
        self,
    ) -> str:
        ret = f"<{self.tag}"
        attr = " ".join(f'{k}="{v.strip()}"' for k, v in self.attr.items())
        if attr:
            ret += f" {attr}"
        ret += ">"
        return ret

    @property
    def end(
        self,
    ) -> str:
        return f"</{self.tag}>"

    def __str__(
        self,
    ):
        """Return the start tag as string representation."""
        return self.start

    def tostring(
        self,
    ) -> str:
        """Return the string serialization of the element."""
        return lxml.etree.tostring(
            self._ele,
            encoding="unicode",
        )

    def text(
        self,
    ) -> List[str]:
        """Return a list of direct text nodes under this element."""
        return self._ele.xpath("./text()")

    def string(
        self,
    ) -> str:
        """Return the string value of this element and all its descendants."""
        return self._ele.xpath("string(.)")

    def children(
        self,
        element: Union[str, ele],
    ) -> "XPathElementList":
        """Return all direct child elements matching the given tag/expression."""
        if isinstance(element, str):
            element = ele(element)
        return XPathElementList(self._ele.xpath(f"./{element}"))

    def child(
        self,
        element: Union[str, ele],
    ) -> "XPathElement":
        """Return the first direct child element matching the given tag/expression."""
        return self.children(element).one()

    def descendants(
        self,
        element: Union[str, ele],
    ) -> "XPathElementList":
        """Return all descendant elements matching the given tag/expression."""
        if isinstance(element, str):
            element = ele(element)
        return XPathElementList(self._ele.xpath(f".//{element}"))

    def descendant(
        self,
        element: Union[str, ele],
    ) -> "XPathElement":
        """Return the first descendant element matching the given tag/expression."""
        return self.descendants(element).one()

    def xpath(
        self,
        string: str,
    ) -> "XPathElementList":
        """Run an arbitrary XPath query and return the results as XPathElementList."""
        return XPathElementList(self._ele.xpath(string))

    def parent(
        self,
    ) -> "XPathElement":
        """Return the parent element as XPathElement."""
        return self.xpath("..").one()

    def next_sibling(
        self,
    ) -> Optional["XPathElement"]:
        """Return the next sibling element, or None if not found."""
        sibs = self._ele.itersiblings()
        for sib in sibs:
            return XPathElement(sib)
        return None

    def prev_sibling(
        self,
    ) -> Optional["XPathElement"]:
        """Return the previous sibling element, or None if not found."""
        sibs = self._ele.itersiblings(preceding=True)
        for sib in sibs:
            return XPathElement(sib)
        return None

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """Check if the element has the given attribute."""
        return name in self._ele.attrib

    def __getitem__(
        self,
        key: str,
    ) -> Optional[str]:
        """Get the value of the given attribute, or None if not present."""
        return self._ele.attrib.get(key)

    def __setitem__(
        self,
        key: str,
        val: str,
    ) -> None:
        self._ele.attrib[key] = val

    def remove(
        self,
        child: "XPathElement",
    ) -> None:
        """Remove the given child element from this element."""
        try:
            self._ele.remove(child._ele)
        except ValueError as e:
            raise XPathModificationError(
                "Element is not a child of this element"
            ) from e

    def clear(
        self,
    ):
        """Remove all child elements and text from this element."""
        self._ele.clear()

    def append(
        self,
        child: "XPathElement",
    ) -> None:
        """Append a child element to this element."""
        self._ele.append(child._ele)

    def insert(
        self,
        index: int,
        child: "XPathElement",
    ) -> None:
        """Insert a child element at the given position."""
        self._ele.insert(index, child._ele)


class XPathElementList:
    """
    A list-like wrapper for multiple XPathElement objects, supporting batch operations.
    """

    def __init__(
        self,
        elements: Iterable[lxml.etree._Element],
    ):
        """Initialize a list of XPathElement objects from an iterable of lxml elements."""
        self._eles = [XPathElement(e) for e in elements]

    def __str__(
        self,
    ):
        """Return string representation of the list of elements."""
        return str([str(e) for e in self._eles])

    def __len__(
        self,
    ) -> int:
        """Return the number of elements in the list."""
        return len(self._eles)

    def len(
        self,
    ) -> int:
        return len(self._eles)

    def empty(
        self,
    ) -> bool:
        """Return True if the list is empty, else False."""
        return len(self) == 0

    def one(
        self,
    ) -> XPathElement:
        if self.empty():
            raise XPathSelectionError("No elements in group")
        if self.len() != 1:
            raise XPathSelectionError(
                "Element list does not contain exactly one element"
            )
        return self._eles[0]

    def first(
        self,
    ) -> XPathElement:
        if self.empty():
            raise XPathSelectionError("No elements in group")
        return self._eles[0]

    def last(
        self,
    ) -> XPathElement:
        if self.empty():
            raise XPathError("No elements in group")
        return self._eles[-1]

    def __getitem__(
        self,
        index: int,
    ) -> XPathElement:
        """Get the element at the specified index."""
        return self._eles[index]

    def filter(
        self,
        func: Callable[[XPathElement], bool],
    ) -> "XPathElementList":
        """Return a new XPathElementList filtered by the given function."""
        return XPathElementList([e._ele for e in self._eles if func(e)])

    def map(
        self,
        func: Callable[[XPathElement], Any],
    ) -> List[Any]:
        """Apply a function to each element and return a list of results."""
        return [func(e) for e in self._eles]

    def for_each(
        self,
        func: Callable[[XPathElement], None],
    ) -> None:
        """Apply a function to each element (no return)."""
        for e in self._eles:
            func(e)

    def to_list(
        self,
    ) -> List[XPathElement]:
        """Return the underlying list of XPathElement objects."""
        return self._eles


def xpath(
    content: Union[str, bytes],
    encoding: str = "utf-8",
) -> XPathElement:
    """Parse HTML content and return the root XPathElement."""
    parser = lxml.etree.HTMLParser(encoding=encoding)
    tree = lxml.etree.HTML(content, parser=parser)
    return XPathElement(tree)
