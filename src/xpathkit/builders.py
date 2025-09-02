from .expressions import attr, dot, ele, fun


class _elebuilder:
    """
    A convenient builder for common HTML element XPath expressions.
    Provides properties for standard tags (div, span, ul, etc.) and supports custom tags via __call__.
    Example: E.div / E.span, E("custom")
    """

    @property
    def root(self) -> ele:
        return ele(".")

    @property
    def parent(self) -> ele:
        return ele("..")

    @property
    def html(self) -> ele:
        return ele("html")

    @property
    def head(self) -> ele:
        return ele("head")

    @property
    def body(self) -> ele:
        return ele("body")

    @property
    def div(self) -> ele:
        return ele("div")

    @property
    def span(self) -> ele:
        return ele("span")

    @property
    def header(self) -> ele:
        return ele("header")

    @property
    def footer(self) -> ele:
        return ele("footer")

    @property
    def main(self) -> ele:
        return ele("main")

    @property
    def section(self) -> ele:
        return ele("section")

    @property
    def article(self) -> ele:
        return ele("article")

    @property
    def nav(self) -> ele:
        return ele("nav")

    @property
    def aside(self) -> ele:
        return ele("aside")

    @property
    def p(self) -> ele:
        return ele("p")

    @property
    def h1(self) -> ele:
        return ele("h1")

    @property
    def h2(self) -> ele:
        return ele("h2")

    @property
    def h3(self) -> ele:
        return ele("h3")

    @property
    def h4(self) -> ele:
        return ele("h4")

    @property
    def h5(self) -> ele:
        return ele("h5")

    @property
    def h6(self) -> ele:
        return ele("h6")

    @property
    def strong(self) -> ele:
        return ele("strong")

    @property
    def em(self) -> ele:
        return ele("em")

    @property
    def b(self) -> ele:
        return ele("b")

    @property
    def i(self) -> ele:
        return ele("i")

    @property
    def a(self) -> ele:
        return ele("a")

    @property
    def img(self) -> ele:
        return ele("img")

    @property
    def ul(self) -> ele:
        return ele("ul")

    @property
    def ol(self) -> ele:
        return ele("ol")

    @property
    def li(self) -> ele:
        return ele("li")

    @property
    def table(self) -> ele:
        return ele("table")

    @property
    def thead(self) -> ele:
        return ele("thead")

    @property
    def tbody(self) -> ele:
        return ele("tbody")

    @property
    def tr(self) -> ele:
        return ele("tr")

    @property
    def th(self) -> ele:
        return ele("th")

    @property
    def td(self) -> ele:
        return ele("td")

    @property
    def form(self) -> ele:
        return ele("form")

    @property
    def input(self) -> ele:
        return ele("input")

    @property
    def button(self) -> ele:
        return ele("button")

    @property
    def textarea(self) -> ele:
        return ele("textarea")

    @property
    def selct(self) -> ele:
        return ele("selct")

    @property
    def option(self) -> ele:
        return ele("option")

    @property
    def label(self) -> ele:
        return ele("label")

    @property
    def any(self) -> ele:
        return ele("*")

    def __call__(
        self,
        tag: str,
    ) -> ele:
        """Initialize an element for XPath expressions."""
        return ele(tag)


class _attrbuilder:
    """
    A convenient builder for common HTML attribute XPath expressions.
    Provides properties for standard attributes (id, class, href, etc.) and supports custom attributes via __call__.
    Example: A.id == "main", A("data-id") == "123"
    """

    @property
    def id(self) -> attr:
        return attr("id")

    @property
    def class_(self) -> attr:
        return attr("class")

    @property
    def style(self) -> attr:
        return attr("style")

    @property
    def title(self) -> attr:
        return attr("title")

    @property
    def href(self) -> attr:
        return attr("href")

    @property
    def src(self) -> attr:
        return attr("src")

    @property
    def alt(self) -> attr:
        return attr("alt")

    @property
    def name(self) -> attr:
        return attr("name")

    @property
    def type(self) -> attr:
        return attr("type")

    @property
    def value(self) -> attr:
        return attr("value")

    @property
    def placeholder(self) -> attr:
        return attr("placeholder")

    @property
    def disabled(self) -> attr:
        return attr("disabled")

    @property
    def checked(self) -> attr:
        return attr("checked")

    @property
    def selected(self) -> attr:
        return attr("selected")

    @property
    def for_(self) -> attr:
        return attr("for")

    @property
    def rel(self) -> attr:
        return attr("rel")

    @property
    def target(self) -> attr:
        return attr("target")

    @property
    def action(self) -> attr:
        return attr("action")

    @property
    def method(self) -> attr:
        return attr("method")

    @property
    def width(self) -> attr:
        return attr("width")

    @property
    def height(self) -> attr:
        return attr("height")

    @property
    def colspan(self) -> attr:
        return attr("colspan")

    @property
    def rowspan(self) -> attr:
        return attr("rowspan")

    def __call__(
        self,
        name: str,
    ) -> attr:
        """Initialize a custom attribute for XPath expressions."""
        return attr(name)


class _funcbuilder:
    """
    A builder for common XPath function calls.
    Provides methods for standard XPath functions and supports custom functions via __call__.
    """

    def position(self, *args):
        return fun("position", *args)

    def last(self, *args):
        return fun("last", *args)

    def count(self, *args):
        return fun("count", *args)

    def id(self, *args):
        return fun("id", *args)

    def local_name(self, *args):
        return fun("local-name", *args)

    def name(self, *args):
        return fun("name", *args)

    def namespace_uri(self, *args):
        return fun("namespace-uri", *args)

    def current(self, *args):
        return fun("current", *args)

    def string(self, *args):
        return fun("string", *args)

    def concat(self, *args):
        return fun("concat", *args)

    def contains(self, *args):
        return fun("contains", *args)

    def starts_with(self, *args):
        return fun("starts-with", *args)

    def ends_with(self, *args):
        return fun("ends-with", *args)

    def substring(self, *args):
        return fun("substring", *args)

    def substring_before(self, *args):
        return fun("substring-before", *args)

    def substring_after(self, *args):
        return fun("substring-after", *args)

    def normalize_space(self, *args):
        return fun("normalize-space", *args)

    def string_length(self, *args):
        return fun("string-length", *args)

    def translate(self, *args):
        return fun("translate", *args)

    def text(self, *args):
        return fun("text", *args)

    def string_join(self, *args):
        return fun("string-join", *args)

    def matches(self, *args):
        return fun("matches", *args)

    def replace(self, *args):
        return fun("replace", *args)

    def boolean(self, *args):
        return fun("boolean", *args)

    def not_(self, *args):
        return fun("not", *args)

    def true(self, *args):
        return fun("true", *args)

    def false(self, *args):
        return fun("false", *args)

    def lang(self, *args):
        return fun("lang", *args)

    def number(self, *args):
        return fun("number", *args)

    def sum(self, *args):
        return fun("sum", *args)

    def floor(self, *args):
        return fun("floor", *args)

    def ceiling(self, *args):
        return fun("ceiling", *args)

    def round(self, *args):
        return fun("round", *args)

    def min(self, *args):
        return fun("min", *args)

    def max(self, *args):
        return fun("max", *args)

    def avg(self, *args):
        return fun("avg", *args)

    def __call__(
        self,
        *args,
        name: str,
    ):
        """Initialize a function call for XPath expressions."""
        return fun(name, *args)


E = _elebuilder()
A = _attrbuilder()
F = _funcbuilder()
