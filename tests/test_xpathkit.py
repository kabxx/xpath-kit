import lxml.etree
import pytest

from xpathkit import (
    A,
    E,
    F,
    XPathElement,
    XPathError,
    XPathModificationError,
    XPathSelectionError,
    attr,
    dot,
    ele,
    fun,
    html,
)


@pytest.fixture
def html_doc():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <div id="main" class="container main-content">
                <h1>Welcome</h1>
                <p>This is a paragraph with a <a href="/link1" class="link active">link</a>.</p>
                <ul id="list">
                    <li class="item active">Item 1</li>
                    <li class="item">Item 2</li>
                    <li class="item special">
                        Item 3
                        <span>- nested</span>
                    </li>
                    <li class="item disabled">Item 4</li>
                </ul>
                <div id="footer" class="container">
                    <p>Footer text. &copy; 2025</p>
                    <a href="/link2" class="link">Another link</a>
                </div>
            </div>
        </body>
    </html>
    """


@pytest.mark.parametrize(
    "expr,expected",
    [
        (ele("div"), "div"),
        (ele("div") / "p", "div/p"),
        (ele("div") / ele("p"), "div/p"),
        (ele("div") / "p" / "a", "div/p/a"),
        (ele("body") // "a", "body//a"),
        (ele("body") // ele("a"), "body//a"),
        (ele("div")[attr("id") == "main"], 'div[@id="main"]'),
        (
            ele("li")[attr("class").any("item", "special")],
            'li[(contains(@class,"item") or contains(@class,"special"))]',
        ),
        (
            ele("div")[attr("class").all("container", "main-content")],
            'div[(contains(@class,"container") and contains(@class,"main-content"))]',
        ),
        (
            ele("li")[attr("class").none("disabled", "hidden")],
            'li[(not(contains(@class,"disabled")) and not(contains(@class,"hidden")))]',
        ),
        (ele("a")[attr("href")], "a[@href]"),
        (
            ele("a")[(attr("class") == "link") & (attr("href") == "/link1")],
            'a[(@class="link" and @href="/link1")]',
        ),
        (
            ele("div")[(attr("id") == "main") | (attr("id") == "footer")],
            'div[(@id="main" or @id="footer")]',
        ),
        (ele("li")[1], "li[1]"),
        (ele("ul") / ele("li")[2], "ul/li[2]"),
        (ele("li")[-1], "li[last()]"),
        (ele("li")[-2], "li[last()-1]"),
        (E.p[dot() == "Welcome"], 'p[.="Welcome"]'),
        (E.p[F.contains(dot(), "Footer")], 'p[contains(.,"Footer")]'),
        (E.li[F.string_length(dot()) > 5], "li[string-length(.)>5]"),
        (
            E.li[F.not_(F.contains(A.class_, "disabled"))],
            'li[not(contains(@class,"disabled"))]',
        ),
        (ele("li")[attr("class").any("item")][1], 'li[(contains(@class,"item"))][1]'),
        (
            ele("div")[attr("id") == "main"]
            // ele("li")[attr("class").all("item", "special")]
            / "span",
            'div[@id="main"]//li[(contains(@class,"item") and contains(@class,"special"))]/span',
        ),
    ],
)
def test_xpath_expression_building(expr, expected):
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (E.div, "div"),
        (E.span, "span"),
        (E.a[A.href == "/home"], 'a[@href="/home"]'),
        (
            E.ul / E.li[A.class_.any("item", "active")],
            'ul/li[(contains(@class,"item") or contains(@class,"active"))]',
        ),
        (E("custom")[A("data-id") == "123"], 'custom[@data-id="123"]'),
        (A.id == "main", '@id="main"'),
        (
            A.class_.any("item", "active"),
            '(contains(@class,"item") or contains(@class,"active"))',
        ),
        (A("data-role") == "button", '@data-role="button"'),
        (A.class_, "@class"),
        (A.for_, "@for"),
        (F.last(), "last()"),
        (F.position(), "position()"),
        (F.contains(A.class_, "active"), 'contains(@class,"active")'),
        (F.normalize_space(dot()) == "Item 1", 'normalize-space(.)="Item 1"'),
        (F.not_(A.disabled), "not(@disabled)"),
    ],
)
def test_xpath_builders(expr, expected):
    assert str(expr) == expected


def test_custom_tag_and_attr():
    elmt = html('<root><foo data-x="1"/></root>').descendant(
        E("foo")[A("data-x") == "1"]
    )
    assert elmt.tag == "foo"


class TestElementQueries:
    """Test query execution and XPathElement object functionality"""

    def test_no_match_raises(self, html_doc):
        root = html(html_doc)
        with pytest.raises(XPathSelectionError):
            root.descendant(E.div[A.id == "not-exist"])

    def test_last_and_negative_index(self, html_doc):
        root = html(html_doc)
        last_li = root.descendant(E.li[-1])
        assert "disabled" in last_li["class"]

    def test_text_and_dot_difference(self):
        html_str = "<div>foo<span>bar</span></div>"
        root = html(html_str)
        div = root.descendant(E.div)
        assert div.text() == ["foo"]
        assert "foobar" in div.string()

    def test_xpathelementlist_methods(self, html_doc):
        root = html(html_doc)
        items = root.descendants(E.li)
        assert items.len() == 4
        assert items.first().tag == "li"
        assert items.last().tag == "li"
        assert isinstance(items.to_list(), list)

    def test_parse_and_root_tag(self, html_doc):
        root = html(html_doc)
        assert isinstance(root, XPathElement)
        assert root.tag == "html"

        root_bytes = html(html_doc.encode("utf-8"), encoding="utf-8")
        assert root_bytes.tag == "html"

    def test_descendant(self, html_doc):
        root = html(html_doc)
        h1 = root.descendant("h1")
        assert h1.tag == "h1"
        assert h1.string() == "Welcome"

        link = root.descendant(ele("a")[attr("class").any("active")])
        assert link["href"] == "/link1"

    def test_child(self, html_doc):
        root = html(html_doc)
        body = root.child("body")
        assert body.tag == "body"

        main_div = body.child(ele("div")[attr("id") == "main"])
        assert "main-content" in main_div["class"]

    def test_string_and_text_and_normalize_space(self, html_doc):
        root = html(html_doc)
        special_li = root.descendant(E.li[A.class_.any("special")])

        cleaned_string = " ".join(special_li.string().split())
        assert cleaned_string == "Item 3 - nested"

        direct_texts = [t.strip() for t in special_li.text() if t.strip()]
        assert direct_texts == ["Item 3"]

        query = E.li[F.normalize_space(dot()) == "Item 3 - nested"]
        print(query)
        found_li = root.descendant(query)
        assert found_li is not None
        assert found_li["class"] == "item special"

    def test_attributes(self, html_doc):
        root = html(html_doc)
        main_div = root.descendant(ele("div")[attr("id") == "main"])
        assert main_div["id"] == "main"
        assert main_div.attr["class"] == "container main-content"
        assert "class" in main_div
        assert "data-test" not in main_div

    def test_parent(self, html_doc):
        root = html(html_doc)
        h1 = root.descendant("h1")
        parent = h1.parent()
        assert parent.tag == "div"
        assert parent["id"] == "main"

    def test_siblings(self, html_doc):
        root = html(html_doc)
        items = root.descendants(E.li)
        item1, item2, item3, item4 = items.to_list()

        assert item1.next_sibling().string() == "Item 2"
        assert item2.next_sibling().string().strip().startswith("Item 3")
        assert item4.next_sibling() is None

        assert item2.prev_sibling().string() == "Item 1"
        assert item1.prev_sibling() is None

    def test_get_set_contains_attribute_edge_cases(self, html_doc):
        root = html(html_doc)
        div = root.descendant(ele("body") / "div")

        assert div["not-exist"] is None

        div["data-new"] = "abc"
        assert div["data-new"] == "abc"

        assert "data-new" in div
        assert "not-exist" not in div


class TestElementList:
    """Test the functionality of XPathElementList objects"""

    def test_list_length_and_emptiness(self, html_doc):
        root = html(html_doc)
        items = root.descendants(ele("li"))
        assert len(items) == 4
        assert items.len() == 4
        assert not items.empty()

        non_existent = root.descendants("divvy")
        assert len(non_existent) == 0
        assert non_existent.empty()

    def test_first_last_one(self, html_doc):
        root = html(html_doc)
        items = root.descendants(ele("li"))
        assert items.first().string() == "Item 1"
        assert items.last().string().strip() == "Item 4"

        h1_list = root.descendants("h1")
        assert len(h1_list) == 1
        assert h1_list.one().string() == "Welcome"

    def test_indexing(self, html_doc):
        root = html(html_doc)
        items = root.descendants(ele("li"))
        assert items[0].string() == "Item 1"
        assert items[2].string().strip().startswith("Item 3")

        assert items[-1].string().strip() == "Item 4"
        assert items[-2].string().strip().startswith("Item 3")

    def test_map_and_filter(self, html_doc):
        root = html(html_doc)
        items = root.descendants(ele("li"))

        all_classes = items.map(lambda item: item["class"])
        assert "item active" in all_classes
        assert "item special" in all_classes

        filtered_items = items.filter(
            lambda item: "active" in item["class"] or "special" in item["class"]
        )
        assert len(filtered_items) == 2

    def test_to_list(self, html_doc):
        root = html(html_doc)
        items = root.descendants(ele("li"))
        py_list = items.to_list()
        assert isinstance(py_list, list)
        assert len(py_list) == 4
        assert isinstance(py_list[0], XPathElement)

    def test_filter_map_on_empty_list(self, html_doc):
        root = html(html_doc)
        items = root.descendants("non-existent-tag")
        assert items.filter(lambda x: True).empty()
        assert items.map(lambda x: x.tag) == []

    def test_elementlist_index_out_of_range(self, html_doc):
        root = html(html_doc)
        items = root.descendants("li")
        with pytest.raises(IndexError):
            _ = items[100]
        with pytest.raises(IndexError):
            _ = items[-100]


class TestErrorHandling:
    """Test expected errors and exceptions"""

    def test_one_on_multiple_elements_raises_error(self, html_doc):
        root = html(html_doc)
        items = root.descendants("li")
        with pytest.raises(XPathSelectionError, match="exactly one element"):
            items.one()

    def test_one_on_empty_list_raises_error(self, html_doc):
        root = html(html_doc)
        items = root.descendants("non-existent-tag")
        with pytest.raises(XPathSelectionError, match="No elements in group"):
            items.one()

    def test_child_on_no_match_raises_error(self, html_doc):
        root = html(html_doc)
        with pytest.raises(XPathSelectionError):
            root.child("non-existent-tag")

    def test_descendant_on_no_match_raises_error(self, html_doc):
        root = html(html_doc)
        with pytest.raises(XPathSelectionError):
            root.descendant("non-existent-tag")

    def test_first_on_empty_list_raises_error(self, html_doc):
        root = html(html_doc)
        items = root.descendants("non-existent-tag")
        with pytest.raises(XPathSelectionError, match="No elements in group"):
            items.first()

    def test_last_on_empty_list_raises_error(self, html_doc):
        root = html(html_doc)
        items = root.descendants("non-existent-tag")
        with pytest.raises(XPathError, match="No elements in group"):
            items.last()


class TestDOMManipulation:
    """Test modification operations on XML/HTML trees"""

    def test_create_and_append_element(self, html_doc):
        root = html(html_doc)
        ul = root.descendant(ele("ul")[attr("id") == "list"])
        assert len(ul.children("li")) == 4

        new_li = XPathElement.create("li", attr={"class": "item new"}, text="Item 5")
        ul.append(new_li)

        li_list = ul.children("li")
        assert len(li_list) == 5
        assert li_list.last().string() == "Item 5"

    def test_remove_element(self, html_doc):
        root = html(html_doc)
        ul = root.descendant(ele("ul")[attr("id") == "list"])
        disabled_li = ul.child(ele("li")[attr("class").any("disabled")])
        assert disabled_li is not None
        ul.remove(disabled_li)

        all_li = ul.children("li")
        assert len(all_li) == 3

        with pytest.raises(XPathSelectionError):
            ul.child(ele("li")[attr("class").any("disabled")])

    def test_remove_non_child_raises_error(self, html_doc):
        root = html(html_doc)
        ul = root.descendant(ele("ul")[attr("id") == "list"])
        h1 = root.descendant("h1")
        with pytest.raises(XPathModificationError, match="not a child"):
            ul.remove(h1)

    def test_set_attribute(self, html_doc):
        root = html(html_doc)
        link = root.descendant(ele("a")[attr("href") == "/link2"])
        assert link["class"] == "link"

        link["class"] = "link updated"
        link["data-id"] = "123"

        assert "updated" in link.tostring()
        assert 'data-id="123"' in link.tostring()

    def test_insert_and_clear(self, html_doc):
        root = html(html_doc)
        ul = root.descendant(E.ul)

        item_to_insert = XPathElement.create("li", text="Item 0")
        ul.insert(0, item_to_insert)
        items = ul.children(E.li)
        assert len(items) == 5
        assert items.first().string() == "Item 0"

        assert not items.empty()
        ul.clear()
        assert ul.children(E.li).empty()
        assert ul.string() == ""

    def test_clear_removes_text_and_children(self, html_doc):
        root = html(html_doc)
        div = root.descendant(ele("body") / "div")
        div.clear()
        assert len(div.text()) == 0
        assert div.children("p").empty()


@pytest.mark.parametrize(
    "expr,expected",
    [
        (fun("last"), "last()"),
        (fun("count", A.id), "count(@id)"),
        (fun("contains", dot(), "foo"), 'contains(.,"foo")'),
        (fun("normalize-space", dot()), "normalize-space(.)"),
        (
            fun("string-length", fun("normalize-space", dot())),
            "string-length(normalize-space(.))",
        ),
    ],
)
def test_fun_builder(expr, expected):
    assert str(expr) == expected


def test_xpathelement_xpath_return_types(html_doc):
    root = html(html_doc)

    title = root.xpath("string(//title)")
    assert isinstance(title, str)
    assert "Test Page" in title

    count = root.xpath("count(//li)")
    assert isinstance(count, float)
    assert count == 4.0

    has_h1 = root.xpath("boolean(//h1)")
    assert isinstance(has_h1, bool)
    assert has_h1 is True

    li_list = root.xpath("//li")
    from xpathkit.xpathkit import XPathElementList

    assert isinstance(li_list, XPathElementList)
    assert len(li_list) == 4
    assert all(l.tag == "li" for l in li_list)

    class_list = root.xpath("//li/@class")
    assert isinstance(class_list, list)
    assert all(isinstance(c, str) for c in class_list)
    assert "item active" in class_list


def test_xpathelement_raw_handle(html_doc):
    root = html(html_doc)
    div = root.descendant(ele("div")[attr("id") == "main"])
    raw_ele = div.raw()

    assert isinstance(raw_ele, lxml.etree._Element)
    assert raw_ele.tag == div.tag


def test_xpathelementlist_iter_and_slice(html_doc):
    root = html(html_doc)
    items = root.descendants(ele("li"))

    tags = [item.tag for item in items]
    assert tags == ["li"] * 4

    sliced = items[1:3]
    assert isinstance(sliced, type(items))
    assert len(sliced) == 2
    assert all(item.tag == "li" for item in sliced)
