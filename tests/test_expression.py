import pytest

from xpathkit.exceptions import XPathEvaluationError
from xpathkit.expressions import (
    _any,
    _any_to_expr_in_pred,
    _any_to_xpath_str,
    _index,
    _str,
    attr,
    dot,
    ele,
    expr,
    fun,
)


@pytest.mark.parametrize(
    "val,expected",
    [
        ("hello", "hello"),
        (123, "123"),
        (True, "true"),
        (False, "false"),
        (None, "None"),
    ],
)
def test_any_to_xpath_str(val, expected):
    assert _any_to_xpath_str(val) == expected


@pytest.mark.parametrize(
    "val,expected",
    [
        ("hello", '"hello"'),
        (attr("id"), "@id"),
        (dot() == "world", '.="world"'),
        (123, "123"),
        (True, "true"),
    ],
)
def test_any_to_str_in_expr(val, expected):
    assert expr._any_to_str_in_expr(val) == expected


def test_any_to_el():
    div_el = ele("div")
    assert ele._any_to_expr_in_ele(div_el) is div_el
    assert isinstance(ele._any_to_expr_in_ele("p"), ele)
    assert str(ele._any_to_expr_in_ele("p")) == "p"
    with pytest.raises(XPathEvaluationError):
        ele._any_to_expr_in_ele(123)


def test_any_to_expr():
    attr_expr = attr("id")
    assert _any_to_expr_in_pred(attr_expr) is attr_expr
    assert isinstance(_any_to_expr_in_pred(1), _index)
    assert isinstance(_any_to_expr_in_pred("raw_string"), _str)
    assert isinstance(_any_to_expr_in_pred(True), _any)


class TestAtomNodes:
    """Tests for the simplest expression nodes like indices and raw strings."""


@pytest.mark.parametrize(
    "val,expected",
    [
        (1, "1"),
        (5, "5"),
        (-1, "last()"),
        (-2, "last()-1"),
        (-10, "last()-9"),
    ],
)
def test_index_node(val, expected):
    assert str(_index(val)) == expected


def test_index_zero_raises():
    with pytest.raises(XPathEvaluationError):
        _index(0).part()


@pytest.mark.parametrize(
    "val,expected",
    [
        ("some_raw_predicate", "some_raw_predicate"),
        ("@id and not(@class)", "@id and not(@class)"),
    ],
)
def test_str_node(val, expected):
    assert str(_str(val)) == expected


@pytest.mark.parametrize(
    "val,expected",
    [
        (True, "true"),
        (123, "123"),
    ],
)
def test_any_node(val, expected):
    assert str(_any(val)) == expected


class TestConditionNodes:
    """Tests for predicates: attr, text, func, and their boolean logic."""


@pytest.mark.parametrize(
    "name,expected",
    [
        ("disabled", "@disabled"),
        ("data-custom", "@data-custom"),
    ],
)
def test_attr_existence(name, expected):
    assert str(attr(name)) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (attr("id") == "main", '@id="main"'),
        (attr("id") != "main", '@id!="main"'),
        (attr("count") > 10, "@count>10"),
        (attr("count") < 10, "@count<10"),
        (attr("count") >= 10, "@count>=10"),
        (attr("count") <= 10, "@count<=10"),
    ],
)
def test_attr_comparisons(expr, expected):
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (attr("class").contains("item"), 'contains(@class,"item")'),
        (attr("href").starts_with("https://"), 'starts-with(@href,"https://")'),
        (attr("src").ends_with(".png"), 'ends-with(@src,".png")'),
    ],
)
def test_attr_string_methods(expr, expected):
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (
            attr("class").all("item", "active"),
            '(contains(@class,"item") and contains(@class,"active"))',
        ),
        (
            attr("class").any("item", "active"),
            '(contains(@class,"item") or contains(@class,"active"))',
        ),
        (
            attr("class").none("disabled", "hidden"),
            '(not(contains(@class,"disabled")) and not(contains(@class,"hidden")))',
        ),
    ],
)
def test_attr_multi_value_methods(expr, expected):
    assert str(expr) == expected


def test_attr_chaining_on_same_instance():
    expr = attr("price").gt(100).lt(200)
    assert str(expr) == "(@price>100 and @price<200)"


@pytest.mark.parametrize(
    "expr,expected",
    [
        ((attr("id") == "a") & (attr("class") == "b"), '(@id="a" and @class="b")'),
        ((attr("id") == "a") | (attr("class") == "b"), '(@id="a" or @class="b")'),
    ],
)
def test_boolean_logic_and_or(expr, expected):
    assert str(expr) == expected


def test_boolean_logic_chaining_and_precedence():

    expr1 = (attr("a") == 1) & (attr("b") == 2) | (attr("c") == 3)
    assert str(expr1) == "((@a=1 and @b=2) or @c=3)"
    expr2 = (attr("a") == 1) | (attr("b") == 2) & (attr("c") == 3)
    assert str(expr2) == "(@a=1 or (@b=2 and @c=3))"
    expr3 = (attr("a") == 1) & ((attr("b") == 2) | (attr("c") == 3))
    assert str(expr3) == "(@a=1 and (@b=2 or @c=3))"


def test_text_node():
    assert str(dot()) == "."
    assert str(dot() == "Hello World") == '.="Hello World"'
    assert str(dot().contains("World")) == 'contains(.,"World")'


def test_func_node():
    assert str(fun("last")) == "last()"
    assert str(fun("position")) == "position()"
    assert str(fun("count", attr("id"))) == "count(@id)"
    assert str(fun("contains", dot(), "some_text")) == 'contains(.,"some_text")'
    assert str(fun("not", attr("disabled"))) == "not(@disabled)"
    # Nested function
    assert str(fun("not", fun("contains", dot(), "hide"))) == 'not(contains(.,"hide"))'


def test_attr_logical_combiners_and_or():
    # Test case for or_
    expr_or = attr("class").contains("a").or_(lambda c: c.contains("b"))
    assert str(expr_or) == '(contains(@class,"a") or contains(@class,"b"))'

    # Test case for and_
    expr_and = attr("class").starts_with("a").and_(lambda c: c.ends_with("z"))
    assert str(expr_and) == '(starts-with(@class,"a") and ends-with(@class,"z"))'


def test_func_with_various_argument_types():
    assert str(fun("round", 1.5)) == "round(1.5)"
    assert str(fun("concat", "User: ", attr("name"))) == 'concat("User: ",@name)'
    assert str(fun("starts-with", dot(), True)) == "starts-with(.,true)"


class TestElementNode:
    """Tests for the 'el' class, which represents HTML/XML elements and paths."""

    def test_el_simple(self):
        assert str(ele("div")) == "div"
        assert str(ele("my-custom-tag")) == "my-custom-tag"

    def test_el_with_axis(self):
        assert str(ele("div", axis="parent")) == "parent::div"
        assert str(ele("*", axis="ancestor")) == "ancestor::*"

    def test_el_path_selectors(self):
        assert str(ele("div") / "p") == "div/p"
        assert str(ele("div") // ele("a")) == "div//a"
        assert str(ele("body") / "div" // "p") == "body/div//p"

    def test_el_with_predicates(self):
        # Integer predicate
        assert str(ele("li")[1]) == "li[1]"
        assert str(ele("li")[-1]) == "li[last()]"
        # Attribute predicate
        assert str(ele("a")[attr("href") == "#"]) == 'a[@href="#"]'
        # Text predicate
        assert str(ele("p")[dot() == "hi"]) == 'p[.="hi"]'
        # Function predicate
        assert str(ele("div")[fun("position") == 1]) == "div[position()=1]"
        # Raw string predicate
        assert str(ele("div")["@id and not(@class)"]) == "div[@id and not(@class)]"

    def test_el_with_multiple_predicates(self):
        # Chaining [] operators adds multiple predicates
        expr = ele("input")[attr("type") == "checkbox"][attr("checked")]
        assert str(expr) == 'input[@type="checkbox"][@checked]'

    def test_el_with_axis_and_predicate(self):
        # Find the first ancestor that is a div
        expr = ele("div", axis="ancestor")[1]
        assert str(expr) == "ancestor::div[1]"
        # Find the preceding sibling span that has a 'data-id' attribute
        expr2 = ele("span", axis="preceding-sibling")[attr("data-id")]
        assert str(expr2) == "preceding-sibling::span[@data-id]"

    def test_el_with_axis_and_predicate(self):
        # Find the first ancestor that is a div
        expr = ele("div", axis="ancestor")[1]
        assert str(expr) == "ancestor::div[1]"
        # Find the preceding sibling span that has a 'data-id' attribute
        expr2 = ele("span", axis="preceding-sibling")[attr("data-id")]
        assert str(expr2) == "preceding-sibling::span[@data-id]"


class TestIntegration:
    """Tests complex, realistic queries combining multiple expression types."""

    def test_complex_path_with_predicates(self):
        # //div[@id="main"]/ul/li[contains(@class, "active")]
        query = (
            ele("div")[attr("id") == "main"]
            / "ul"
            / ele("li")[attr("class").contains("active")]
        )
        expected = 'div[@id="main"]/ul/li[contains(@class,"active")]'
        assert str(query) == expected

    def test_descendant_with_multiple_conditions(self):
        # //a[(contains(@href, "example.com")) and (not(@target))]
        query = ele("a")[
            (attr("href").contains("example.com")) & fun("not", attr("target"))
        ]
        expected = 'a[(contains(@href,"example.com") and not(@target))]'
        assert str(query) == expected

    def test_positional_and_attribute_logic(self):
        # //tr[ (td[1] > 100) or (td[2] = 'N/A') ]
        # Note: This requires using raw strings for complex inner queries for now.
        query = ele("tr")["(td[1] > 100) or (td[2] = 'N/A')"]
        expected = "tr[(td[1] > 100) or (td[2] = 'N/A')]"
        assert str(query) == expected

    def test_predicate_with_sub_element(self):
        # //div[./a[@href]]
        query = ele("div")[ele("a")[attr("href")]]
        expected = "div[a[@href]]"
        assert str(query) == expected

    def test_nested_functions_and_text(self):
        # //p[string-length(normalize-space(.)) > 0]
        query = ele("p")[fun("string-length", fun("normalize-space", dot())) > 0]
        expected = "p[string-length(normalize-space(.))>0]"
        assert str(query) == expected

    def test_complex_class_selection(self):
        # //div[ (contains(@class,"widget") and not(contains(@class,"disabled"))) or @id="fallback" ]
        query = ele("div")[
            (
                attr("class").contains("widget")
                & fun("not", attr("class").contains("disabled"))
            )
            | (attr("id") == "fallback")
        ]
        expected = 'div[((contains(@class,"widget") and not(contains(@class,"disabled"))) or @id="fallback")]'
        assert str(query) == expected
