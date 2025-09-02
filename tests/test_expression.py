import pytest
from xpathkit.expressions import (
    expr,
    ele,
    attr,
    dot,
    fun,
    _any_to_xpath_str,
    _any_to_expr,
    _index,
    _str,
    _any,
)
from xpathkit.exceptions import XPathEvaluationError



class TestHelperFunctions:
    """Tests for internal helper functions that convert types."""

    def test_any_to_xpath_str(self):
        assert _any_to_xpath_str("hello") == "hello"
        assert _any_to_xpath_str(123) == "123"
        assert _any_to_xpath_str(True) == "true"
        assert _any_to_xpath_str(False) == "false"
        assert _any_to_xpath_str(None) == "None"

    def test_any_to_str_in_expr(self):
        # Strings should be quoted
        assert expr._any_to_str_in_expr("hello") == '"hello"'
        # Expressions should be rendered
        assert expr._any_to_str_in_expr(attr("id")) == "@id"
        assert expr._any_to_str_in_expr(dot() == "world") == '.="world"'
        # Other types should be converted directly
        assert expr._any_to_str_in_expr(123) == "123"
        assert expr._any_to_str_in_expr(True) == "true"

    def test_any_to_el(self):
        div_el = ele("div")
        assert ele._any_to_expr_in_ele(div_el) is div_el
        assert isinstance(ele._any_to_expr_in_ele("p"), ele)
        assert str(ele._any_to_expr_in_ele("p")) == "p"
        with pytest.raises(XPathEvaluationError):
            ele._any_to_expr_in_ele(123)

    def test_any_to_expr(self):
        attr_expr = attr("id")
        assert _any_to_expr(attr_expr) is attr_expr
        assert isinstance(_any_to_expr(1), _index)
        assert isinstance(_any_to_expr("raw_string"), _str)
        assert isinstance(_any_to_expr(True), _any)


class TestAtomNodes:
    """Tests for the simplest expression nodes like indices and raw strings."""

    def test_index_node(self):
        assert str(_index(1)) == "1"
        assert str(_index(5)) == "5"
        # Negative indexing
        assert str(_index(-1)) == "last()"
        assert str(_index(-2)) == "last()-1"
        assert str(_index(-10)) == "last()-9"
        # Zero is invalid in XPath
        with pytest.raises(XPathEvaluationError):
            _index(0).part()

    def test_str_node(self):
        assert str(_str("some_raw_predicate")) == "some_raw_predicate"
        assert str(_str("@id and not(@class)")) == "@id and not(@class)"

    def test_any_node(self):
        assert str(_any(True)) == "true"
        assert str(_any(123)) == "123"


class TestConditionNodes:
    """Tests for predicates: attr, text, func, and their boolean logic."""

    def test_attr_existence(self):
        assert str(attr("disabled")) == "@disabled"
        assert str(attr("data-custom")) == "@data-custom"

    def test_attr_comparisons(self):
        assert str(attr("id") == "main") == '@id="main"'
        assert str(attr("id") != "main") == '@id!="main"'
        assert str(attr("count") > 10) == "@count>10"
        assert str(attr("count") < 10) == "@count<10"
        assert str(attr("count") >= 10) == "@count>=10"
        assert str(attr("count") <= 10) == "@count<=10"

    def test_attr_string_methods(self):
        assert str(attr("class").contains("item")) == 'contains(@class,"item")'
        assert str(attr("href").starts_with("https://")) == 'starts-with(@href,"https://")'
        assert str(attr("src").ends_with(".png")) == 'ends-with(@src,".png")'

    def test_attr_multi_value_methods(self):
        # all() -> AND logic
        expr_all = attr("class").all("item", "active")
        assert str(expr_all) == '(contains(@class,"item") and contains(@class,"active"))'
        # any() -> OR logic
        expr_any = attr("class").any("item", "active")
        assert str(expr_any) == '(contains(@class,"item") or contains(@class,"active"))'
        # none() -> NOT AND logic
        expr_none = attr("class").none("disabled", "hidden")
        assert str(expr_none) == '(not(contains(@class,"disabled")) and not(contains(@class,"hidden")))'

    def test_attr_chaining_on_same_instance(self):
        # Chaining multiple conditions on the same attribute implies AND
        expr = attr("price").gt(100).lt(200)
        assert str(expr) == "(@price>100 and @price<200)"

    def test_boolean_logic_and_or(self):
        expr_and = (attr("id") == "a") & (attr("class") == "b")
        assert str(expr_and) == '(@id="a" and @class="b")'
        expr_or = (attr("id") == "a") | (attr("class") == "b")
        assert str(expr_or) == '(@id="a" or @class="b")'

    def test_boolean_logic_chaining_and_precedence(self):
        # Your implementation correctly groups expressions left-to-right
        expr1 = (attr("a") == 1) & (attr("b") == 2) | (attr("c") == 3)
        assert str(expr1) == "((@a=1 and @b=2) or @c=3)"

        expr2 = (attr("a") == 1) | (attr("b") == 2) & (attr("c") == 3)
        assert str(expr2) == "(@a=1 or (@b=2 and @c=3))"

        # Explicit grouping with parentheses
        expr3 = (attr("a") == 1) & ((attr("b") == 2) | (attr("c") == 3))
        assert str(expr3) == "(@a=1 and (@b=2 or @c=3))"

    def test_text_node(self):
        assert str(dot()) == "."
        assert str(dot() == "Hello World") == '.="Hello World"'
        assert str(dot().contains("World")) == 'contains(.,"World")'

    def test_func_node(self):
        assert str(fun("last")) == "last()"
        assert str(fun("position")) == "position()"
        assert str(fun("count", attr("id"))) == "count(@id)"
        assert str(fun("contains", dot(), "some_text")) == 'contains(.,"some_text")'
        assert str(fun("not", attr("disabled"))) == "not(@disabled)"
        # Nested function
        assert str(fun("not", fun("contains", dot(), "hide"))) == 'not(contains(.,"hide"))'

    def test_attr_logical_combiners_and_or(self):
        # Test case for or_
        expr_or = attr("class").contains("a").or_(lambda c: c.contains("b"))
        assert str(expr_or) == '(contains(@class,"a") or contains(@class,"b"))'

        # Test case for and_
        expr_and = attr("class").starts_with("a").and_(lambda c: c.ends_with("z"))
        assert str(expr_and) == '(starts-with(@class,"a") and ends-with(@class,"z"))'

    def test_func_with_various_argument_types(self):
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
        query = ele("div")[attr("id") == "main"] / "ul" / ele("li")[attr("class").contains("active")]
        expected = 'div[@id="main"]/ul/li[contains(@class,"active")]'
        assert str(query) == expected

    def test_descendant_with_multiple_conditions(self):
        # //a[(contains(@href, "example.com")) and (not(@target))]
        query = ele("a")[(attr("href").contains("example.com")) & fun("not", attr("target"))]
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
        query = ele("div")[(attr("class").contains("widget") & fun("not", attr("class").contains("disabled"))) | (attr("id") == "fallback")]
        expected = 'div[((contains(@class,"widget") and not(contains(@class,"disabled"))) or @id="fallback")]'
        assert str(query) == expected
