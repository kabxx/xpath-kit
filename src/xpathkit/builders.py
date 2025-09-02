from .expressions import attr, el


class _elbuilder:
    """
    A convenient builder for common HTML element XPath expressions.
    Provides properties for standard tags (div, span, ul, etc.) and supports custom tags via __call__.
    Example: E.div / E.span, E("custom")
    """

    @property
    def html(self) -> el:
        return el("html")

    @property
    def head(self) -> el:
        return el("head")

    @property
    def body(self) -> el:
        return el("body")

    @property
    def div(self) -> el:
        return el("div")

    @property
    def span(self) -> el:
        return el("span")

    @property
    def header(self) -> el:
        return el("header")

    @property
    def footer(self) -> el:
        return el("footer")

    @property
    def main(self) -> el:
        return el("main")

    @property
    def section(self) -> el:
        return el("section")

    @property
    def article(self) -> el:
        return el("article")

    @property
    def nav(self) -> el:
        return el("nav")

    @property
    def aside(self) -> el:
        return el("aside")

    @property
    def p(self) -> el:
        return el("p")

    @property
    def h1(self) -> el:
        return el("h1")

    @property
    def h2(self) -> el:
        return el("h2")

    @property
    def h3(self) -> el:
        return el("h3")

    @property
    def h4(self) -> el:
        return el("h4")

    @property
    def h5(self) -> el:
        return el("h5")

    @property
    def h6(self) -> el:
        return el("h6")

    @property
    def strong(self) -> el:
        return el("strong")

    @property
    def em(self) -> el:
        return el("em")

    @property
    def b(self) -> el:
        return el("b")

    @property
    def i(self) -> el:
        return el("i")

    @property
    def a(self) -> el:
        return el("a")

    @property
    def img(self) -> el:
        return el("img")

    @property
    def ul(self) -> el:
        return el("ul")

    @property
    def ol(self) -> el:
        return el("ol")

    @property
    def li(self) -> el:
        return el("li")

    @property
    def table(self) -> el:
        return el("table")

    @property
    def thead(self) -> el:
        return el("thead")

    @property
    def tbody(self) -> el:
        return el("tbody")

    @property
    def tr(self) -> el:
        return el("tr")

    @property
    def th(self) -> el:
        return el("th")

    @property
    def td(self) -> el:
        return el("td")

    @property
    def form(self) -> el:
        return el("form")

    @property
    def input(self) -> el:
        return el("input")

    @property
    def button(self) -> el:
        return el("button")

    @property
    def textarea(self) -> el:
        return el("textarea")

    @property
    def selct(self) -> el:
        return el("selct")

    @property
    def option(self) -> el:
        return el("option")

    @property
    def label(self) -> el:
        return el("label")

    @property
    def any(self) -> el:
        return el("*")

    def __call__(
        self,
        tag: str,
    ) -> el:
        return el(tag)


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

    def __call__(self, name: str) -> attr:
        return attr(name)


E = _elbuilder()
A = _attrbuilder()
