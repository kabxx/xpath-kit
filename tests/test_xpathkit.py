import pytest
from xpathkit import (
    XPathElement,
    XPathError,
    XPathModificationError,
    XPathSelectionError,
    attr,
    ele,
    expr,
    xpath,
)


# --- Test Fixture ---
# Provide a standard HTML document for all tests to avoid code duplication
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


# --- Test Cases ---


class TestExpressionBuilding:
    """Test if the XPath expression builder generates correct strings"""

    def test_simple_element(self):
        assert str(ele("div")) == "div"

    def test_child_selector(self):
        assert str(ele("div") / "p") == "div/p"
        assert str(ele("div") / ele("p")) == "div/p"
        assert str(ele("div") / "p" / "a") == "div/p/a"

    def test_descendant_selector(self):
        assert str(ele("body") // "a") == "body//a"
        assert str(ele("body") // ele("a")) == "body//a"

    def test_attribute_equals(self):
        assert str(ele("div")[attr("id") == "main"]) == 'div[@id="main"]'

    def test_attribute_any(self):
        query = ele("li")[attr("class").any("item", "special")]
        expected = 'li[(contains(@class,"item") or contains(@class,"special"))]'
        assert str(query) == expected

    def test_attribute_all(self):
        query = ele("div")[attr("class").all("container", "main-content")]
        expected = (
            'div[(contains(@class,"container") and contains(@class,"main-content"))]'
        )
        assert str(query) == expected

    def test_attribute_none(self):
        query = ele("li")[attr("class").none("disabled", "hidden")]
        expected = (
            'li[(not(contains(@class,"disabled")) and not(contains(@class,"hidden")))]'
        )
        assert str(query) == expected

    def test_attribute_exists(self):
        assert str(ele("a")[attr("href")]) == "a[@href]"

    def test_logical_and_or(self):
        query_and = ele("a")[(attr("class") == "link") & (attr("href") == "/link1")]
        assert str(query_and) == 'a[(@class="link" and @href="/link1")]'

        query_or = ele("div")[(attr("id") == "main") | (attr("id") == "footer")]
        assert str(query_or) == 'div[(@id="main" or @id="footer")]'

    def test_positional_predicate(self):
        # XPath indices are 1-based
        assert str(ele("li")[1]) == "li[1]"
        assert str(ele("ul") / ele("li")[2]) == "ul/li[2]"

    def test_multiple_predicates(self):
        query = ele("li")[attr("class").any("item")][1]
        assert str(query) == 'li[(contains(@class,"item"))][1]'

    def test_complex_expression(self):
        query = (
            ele("div")[attr("id") == "main"]
            // ele("li")[attr("class").all("item", "special")]
            / "span"
        )
        expected = 'div[@id="main"]//li[(contains(@class,"item") and contains(@class,"special"))]/span'
        assert str(query) == expected

    def test_expr_predicate(self):
        assert (
            str(ele("p")[expr("text()") == "'Footer text. © 2025'"])
            == "p[(text()='Footer text. © 2025')]"
        )
        assert str(ele("ul")[expr("count(li)") > 3]) == "ul[(count(li)>3)]"


class TestElementQueries:
    """Test query execution and XPathElement object functionality"""

    def test_parse_and_root_tag(self, html_doc):
        root = xpath(html_doc)
        assert isinstance(root, XPathElement)
        assert root.tag == "html"

        root_bytes = xpath(html_doc.encode("utf-8"), encoding="utf-8")
        assert root_bytes.tag == "html"

    def test_descendant(self, html_doc):
        root = xpath(html_doc)
        h1 = root.descendant("h1")
        assert h1.tag == "h1"
        assert h1.string() == "Welcome"

        link = root.descendant(ele("a")[attr("class").any("active")])
        assert link["href"] == "/link1"

    def test_child(self, html_doc):
        root = xpath(html_doc)
        body = root.child("body")
        assert body.tag == "body"

        main_div = body.child(ele("div")[attr("id") == "main"])
        assert "main-content" in main_div["class"]

    def test_string_and_text(self, html_doc):
        root = xpath(html_doc)
        special_li = root.descendant(ele("li")[attr("class").any("special")])
        cleaned_string = " ".join(special_li.string().split())
        assert (
            cleaned_string == "Item 3 - nested"
        )  # Note: there is a space in the middle

        # .text() only returns direct child text nodes
        direct_texts = [t.strip() for t in special_li.text() if t.strip()]
        assert direct_texts == ["Item 3"]

    def test_attributes(self, html_doc):
        root = xpath(html_doc)
        main_div = root.descendant(ele("div")[attr("id") == "main"])
        assert main_div["id"] == "main"
        assert main_div.attr["class"] == "container main-content"
        assert "class" in main_div
        assert "data-test" not in main_div

    def test_parent(self, html_doc):
        root = xpath(html_doc)
        h1 = root.descendant("h1")
        parent = h1.parent()
        assert parent.tag == "div"
        assert parent["id"] == "main"


class TestElementList:
    """Test the functionality of XPathElementList objects"""

    def test_list_length_and_emptiness(self, html_doc):
        root = xpath(html_doc)
        items = root.descendants(ele("li"))
        assert len(items) == 4
        assert items.len() == 4
        assert not items.empty()

        non_existent = root.descendants("divvy")
        assert len(non_existent) == 0
        assert non_existent.empty()

    def test_first_last_one(self, html_doc):
        root = xpath(html_doc)
        items = root.descendants(ele("li"))
        assert items.first().string() == "Item 1"
        assert items.last().string().strip() == "Item 4"

        h1_list = root.descendants("h1")
        assert len(h1_list) == 1
        assert h1_list.one().string() == "Welcome"

    def test_indexing(self, html_doc):
        root = xpath(html_doc)
        items = root.descendants(ele("li"))
        assert items[0].string() == "Item 1"
        assert items[2].string().strip().startswith("Item 3")

    def test_map_and_filter(self, html_doc):
        root = xpath(html_doc)
        items = root.descendants(ele("li"))

        # Map to get all classes
        all_classes = items.map(lambda item: item["class"])
        assert "item active" in all_classes
        assert "item special" in all_classes

        # Filter to get only active or special items
        filtered_items = items.filter(
            lambda item: "active" in item["class"] or "special" in item["class"]
        )
        assert len(filtered_items) == 2

    def test_to_list(self, html_doc):
        root = xpath(html_doc)
        items = root.descendants(ele("li"))
        py_list = items.to_list()
        assert isinstance(py_list, list)
        assert len(py_list) == 4
        assert isinstance(py_list[0], XPathElement)


class TestErrorHandling:
    """Test expected errors and exceptions"""

    def test_one_on_multiple_elements_raises_error(self, html_doc):
        root = xpath(html_doc)
        items = root.descendants("li")
        with pytest.raises(XPathSelectionError, match="exactly one element"):
            items.one()

    def test_one_on_empty_list_raises_error(self, html_doc):
        root = xpath(html_doc)
        items = root.descendants("non-existent-tag")
        with pytest.raises(XPathSelectionError, match="No elements in group"):
            items.one()

    def test_child_on_no_match_raises_error(self, html_doc):
        root = xpath(html_doc)
        with pytest.raises(XPathSelectionError):
            root.child("non-existent-tag")

    def test_descendant_on_no_match_raises_error(self, html_doc):
        root = xpath(html_doc)
        with pytest.raises(XPathSelectionError):
            root.descendant("non-existent-tag")

    def test_first_on_empty_list_raises_error(self, html_doc):
        root = xpath(html_doc)
        items = root.descendants("non-existent-tag")
        with pytest.raises(XPathSelectionError, match="No elements in group"):
            items.first()


class TestDOMManipulation:
    """Test modification operations on XML/HTML trees"""

    def test_create_and_append_element(self, html_doc):
        root = xpath(html_doc)
        ul = root.descendant(ele("ul")[attr("id") == "list"])

        initial_len = len(ul.children("li"))
        assert initial_len == 4

        # Create and append a new element
        new_li = XPathElement.create("li", attr={"class": "item new"}, text="Item 5")
        ul.append(new_li)

        # Verify
        li_list = ul.children("li")
        assert len(li_list) == 5
        assert li_list.last().string() == "Item 5"
        assert li_list.last()["class"] == "item new"

    def test_remove_element(self, html_doc):
        root = xpath(html_doc)
        ul = root.descendant(ele("ul")[attr("id") == "list"])

        disabled_li = ul.child(ele("li")[attr("class").any("disabled")])
        assert disabled_li is not None

        # Remove element
        ul.remove(disabled_li)

        # Verify
        all_li = ul.children("li")
        assert len(all_li) == 3

        # Query again, should not find it
        with pytest.raises(XPathError):
            ul.child(ele("li")[attr("class").any("disabled")])

    def test_remove_non_child_raises_error(self, html_doc):
        root = xpath(html_doc)
        ul = root.descendant(ele("ul")[attr("id") == "list"])
        h1 = root.descendant("h1")

        with pytest.raises(XPathModificationError, match="not a child"):
            ul.remove(h1)

    def test_set_attribute(self, html_doc):
        root = xpath(html_doc)
        link = root.descendant(ele("a")[attr("href") == "/link2"])
        assert link["class"] == "link"

        # 修改属性
        link["class"] = "link updated"
        link["data-id"] = "123"

        # 验证
        assert "updated" in link.tostring()
        assert 'data-id="123"' in link.tostring()
