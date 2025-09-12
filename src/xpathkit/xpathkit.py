from typing import Any, Callable, Dict, Iterable, List, Optional, Union

import lxml
import lxml.etree

from .exceptions import XPathError, XPathModificationError, XPathSelectionError
from .expressions import dot, ele, expr, fun


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
        """Create a new XPathElement."""
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
        """Return the start tag as string representation."""
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
        """Return the end tag as string representation."""
        return f"</{self.tag}>"

    def __str__(
        self,
    ):
        """Return the start tag string of the element (e.g. <tag ...>)."""
        return self.start

    def tostring(
        self,
    ) -> str:
        """Return the full XML serialization of the element as a string."""
        return lxml.etree.tostring(
            self._ele,
            encoding="unicode",
        )

    def text(
        self,
    ) -> List[str]:
        """Return a list of direct text nodes under this element (not including descendants)."""
        return self.xpath(ele(".") / fun("text"))

    def string(
        self,
    ) -> str:
        """Return the concatenated text content of this element and all its descendants."""
        return self.xpath(fun("string", dot()))

    def children(
        self,
        element: Union[str, ele],
    ) -> "XPathElementList":
        """Return all direct children matching the given tag or XPath expression."""
        if isinstance(element, str):
            element = ele(element)
        children = self.xpath(f"./{element}")
        if not isinstance(children, XPathElementList):
            raise XPathSelectionError("XPath expression did not return any elements.")
        return children

    def child(
        self,
        element: Union[str, ele],
    ) -> "XPathElement":
        """Return the first direct child matching the given tag or XPath expression."""
        children = self.children(element)
        if not isinstance(children, XPathElementList):
            raise XPathSelectionError("XPath expression did not return any elements.")
        return children.one()

    def has_single_child(
        self,
        element: Union[str, ele],
    ) -> bool:
        """Return true if there is at least one direct child matching the given tag or XPath expression."""
        return self.children(element).len() == 1

    def has_any_child(
        self,
        element: Union[str, ele],
    ) -> bool:
        """Return true if there is at least one direct child matching the given tag or XPath expression."""
        return self.children(element).len() > 0

    def descendants(
        self,
        element: Union[str, ele],
    ) -> "XPathElementList":
        """Return all descendants matching the given tag or XPath expression."""
        if isinstance(element, str):
            element = ele(element)
        descendants = self.xpath(f".//{element}")
        if not isinstance(descendants, XPathElementList):
            raise XPathSelectionError("XPath expression did not return any elements.")
        return descendants

    def descendant(
        self,
        element: Union[str, ele],
    ) -> "XPathElement":
        """Return the first descendant matching the given tag or XPath expression."""
        descendants = self.descendants(element)
        if not isinstance(descendants, XPathElementList):
            raise XPathSelectionError("XPath expression did not return any elements.")
        return descendants.one()

    def has_single_descendant(
        self,
        element: Union[str, ele],
    ) -> bool:
        """Return true if there is exactly one descendant matching the given tag or XPath expression."""
        return self.descendants(element).len() == 1

    def has_any_descendant(
        self,
        element: Union[str, ele],
    ) -> bool:
        """Return true if there is at least one descendant matching the given tag or XPath expression."""
        return self.descendants(element).len() > 0

    def xpath(
        self,
        val: Union[expr, str],
    ) -> Union["XPathElementList", str, float, bool, List[str]]:
        """Run an arbitrary XPath query and return the results as XPathElementList."""
        res = self._ele.xpath(str(val))
        if isinstance(res, bool):
            return res
        elif isinstance(res, str):
            return res
        elif isinstance(res, float):
            return res
        elif isinstance(res, list):
            if all(isinstance(r, lxml.etree._Element) for r in res):
                return XPathElementList(res)
            elif all(isinstance(r, str) for r in res):
                return res
        raise XPathSelectionError("Unexpected return value from lxml")

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
        key: str,
    ) -> bool:
        """Check if the element has the given attribute."""
        return key in self._ele.attrib

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
        """Set the value of the given attribute."""
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
                "The element to be removed is not a child of this element."
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

    def raw(
        self,
    ) -> lxml.etree._Element:
        """Return the underlying lxml.etree._Element object."""
        return self._ele


class XPathElementList:
    """
    A list-like wrapper for multiple XPathElement objects, supporting batch operations such as filter, map, and iteration.
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
        """Return the number of elements in the list."""
        return len(self._eles)

    def empty(
        self,
    ) -> bool:
        """Return True if the list is empty, else False."""
        return len(self) == 0

    def one(
        self,
    ) -> XPathElement:
        """Return the only element in the list, or raise if the list does not contain exactly one element."""
        if self.empty():
            raise XPathSelectionError("No elements found in the list.")
        if self.len() != 1:
            raise XPathSelectionError(
                "Element list does not contain exactly one element."
            )
        return self._eles[0]

    def first(
        self,
    ) -> XPathElement:
        """Return the first element in the list, or raise if the list is empty."""
        if self.empty():
            raise XPathSelectionError("No elements found in the list.")
        return self._eles[0]

    def last(
        self,
    ) -> XPathElement:
        """Return the last element in the list, or raise if the list is empty."""
        if self.empty():
            raise XPathError("No elements found in the list.")
        return self._eles[-1]

    def __getitem__(
        self,
        key: int,
    ) -> XPathElement:
        """Get the element at the specified index."""
        if isinstance(key, int):
            return self._eles[key]
        elif isinstance(key, slice):
            return XPathElementList(
                [e.raw() for e in self._eles[key.start : key.stop : key.step]]
            )
        else:
            raise TypeError

    def filter(
        self,
        func: Callable[[XPathElement], bool],
    ) -> "XPathElementList":
        """Return a new XPathElementList containing elements for which func(element) is True."""
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
        """Apply a function to each element in the list. Does not return anything."""
        for e in self._eles:
            func(e)

    def to_list(
        self,
    ) -> List[XPathElement]:
        """Return the underlying list of XPathElement objects."""
        return self._eles

    def __iter__(
        self,
    ):
        """Return an iterator over the elements."""
        return iter(self._eles)


def html(
    content: Optional[Union[str, bytes]] = None,
    path: Optional[str] = None,
    encoding: str = "utf-8",
) -> XPathElement:
    """
    Parse HTML content or file and return the root XPathElement.

    Args:
        content: HTML content as a string or bytes.
        path: Path to the HTML file.
        encoding: Encoding to use if content is a string.
    Returns:
        XPathElement: The root element of the parsed HTML.
    Raises:
        ValueError: If neither or both content and path are provided.
        XPathError: If parsing fails.
    """
    if not content and not path:
        raise ValueError("Either 'content' or 'path' must be provided.")
    if content and path:
        raise ValueError("Only one of 'content' or 'path' can be provided, not both.")

    if not content:
        with open(path, "rb") as f:
            content = f.read()

    if isinstance(content, str):
        content = content.encode(encoding)

    try:
        tree = lxml.etree.HTML(content)
        return XPathElement(tree)
    except lxml.etree.LxmlError as e:
        raise XPathError(f"Failed to parse HTML content: {e}")


def xml(
    content: Optional[Union[str, bytes]] = None,
    path: Optional[str] = None,
    encoding: str = "utf-8",
) -> XPathElement:
    """
    Parse XML content or file and return the root XPathElement.

    Args:
        content: XML content as a string or bytes.
        path: Path to the XML file.
        encoding: Encoding to use if content is a string.
    Returns:
        XPathElement: The root element of the parsed XML.
    Raises:
        ValueError: If neither or both content and path are provided.
        XPathError: If parsing fails.
    """
    if not content and not path:
        raise ValueError("Either 'content' or 'path' must be provided.")
    if content and path:
        raise ValueError("Only one of 'content' or 'path' can be provided, not both.")

    if not content:
        with open(path, "rb") as f:
            content = f.read()

    if isinstance(content, str):
        content = content.encode(encoding)

    try:
        tree = lxml.etree.XML(content)
        return XPathElement(tree)
    except lxml.etree.LxmlError as e:
        raise XPathError(f"Failed to parse XML content: {e}")
