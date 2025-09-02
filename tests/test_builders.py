import pytest
from xpathkit.builders import E, A, F
from xpathkit.expressions import ele, attr, fun, dot


class TestElementBuilder:
    """Tests for the E (_elbuilder) singleton."""

    @pytest.mark.parametrize(
        "prop_name, expected_tag",
        [
            ("div", "div"),
            ("p", "p"),
            ("a", "a"),
            ("h1", "h1"),
            ("li", "li"),
            ("table", "table"),
            ("span", "span"),
            ("img", "img"),
            ("form", "form"),
            ("input", "input"),
            ("button", "button"),
        ],
    )
    def test_common_element_properties(self, prop_name, expected_tag):
        """Test that common element properties like E.div create correct ele objects."""
        element_expr = getattr(E, prop_name)
        assert isinstance(element_expr, ele)
        assert str(element_expr) == expected_tag

    def test_special_element_properties(self):
        """Test special properties like any, parent, and root."""
        assert isinstance(E.any, ele)
        assert str(E.any) == "*"

        assert isinstance(E.parent, ele)
        assert str(E.parent) == ".."

        assert isinstance(E.root, ele)
        assert str(E.root) == "."

    def test_callable_for_custom_tags(self):
        """Test creating custom element tags using E('custom-tag')."""
        custom_el = E("my-custom-element")
        assert isinstance(custom_el, ele)
        assert str(custom_el) == "my-custom-element"

        another_custom_el = E("svg:path")
        assert isinstance(another_custom_el, ele)
        assert str(another_custom_el) == "svg:path"


class TestAttributeBuilder:
    """Tests for the A (_attrbuilder) singleton."""

    @pytest.mark.parametrize(
        "prop_name, expected_attr",
        [
            ("id", "@id"),
            ("style", "@style"),
            ("title", "@title"),
            ("href", "@href"),
            ("src", "@src"),
            ("alt", "@alt"),
            ("name", "@name"),
            ("type", "@type"),
            ("value", "@value"),
            ("placeholder", "@placeholder"),
            ("disabled", "@disabled"),
            ("checked", "@checked"),
            ("selected", "@selected"),
            ("rel", "@rel"),
            ("target", "@target"),
        ],
    )
    def test_common_attribute_properties(self, prop_name, expected_attr):
        """Test that common attribute properties like A.id create correct attr objects."""
        attr_expr = getattr(A, prop_name)
        assert isinstance(attr_expr, attr)
        # The `part()` method of an attr object without conditions should be its name.
        assert attr_expr.part() == expected_attr

    def test_keyword_attribute_properties(self):
        """Test attributes that are Python keywords, like 'class' and 'for'."""
        class_attr = A.class_
        assert isinstance(class_attr, attr)
        assert str(class_attr) == "@class"

        for_attr = A.for_
        assert isinstance(for_attr, attr)
        assert str(for_attr) == "@for"

    def test_callable_for_custom_attributes(self):
        """Test creating custom attributes using A('data-id')."""
        custom_attr = A("data-testid")
        assert isinstance(custom_attr, attr)
        assert str(custom_attr) == "@data-testid"

        namespaced_attr = A("xml:lang")
        assert isinstance(namespaced_attr, attr)
        assert str(namespaced_attr) == "@xml:lang"


class TestFunctionBuilder:
    """Tests for the F (_funcbuilder) singleton."""

    def test_functions_with_no_args(self):
        """Test functions that typically take no arguments, like position() and last()."""
        assert isinstance(F.position(), fun)
        assert str(F.position()) == "position()"

        assert isinstance(F.last(), fun)
        assert str(F.last()) == "last()"

        assert isinstance(F.true(), fun)
        assert str(F.true()) == "true()"

        assert isinstance(F.false(), fun)
        assert str(F.false()) == "false()"

    def test_functions_with_one_arg(self):
        """Test functions that take one argument."""
        # Argument is an attribute expression
        count_expr = F.count(A.id)
        assert isinstance(count_expr, fun)
        assert str(count_expr) == "count(@id)"

        # Argument is a . expression
        norm_space_expr = F.normalize_space(dot())
        assert isinstance(norm_space_expr, fun)
        assert str(norm_space_expr) == "normalize-space(.)"

        # Argument is a string literal
        lang_expr = F.lang("en")
        assert str(lang_expr) == 'lang("en")'

    def test_functions_with_multiple_args(self):
        """Test functions that take multiple arguments of various types."""
        # String and attr args
        contains_expr = F.contains(A.class_, "item")
        assert str(contains_expr) == 'contains(@class,"item")'

        # String and number args
        substring_expr = F.substring("hello world", 1, 5)
        assert str(substring_expr) == 'substring("hello world",1,5)'

        # Multiple string args
        concat_expr = F.concat("a", "b", "c")
        assert str(concat_expr) == 'concat("a","b","c")'

    def test_not_function_handling(self):
        """Test the special-cased `not_` method."""
        not_expr = F.not_(A.disabled)
        assert isinstance(not_expr, fun)
        assert str(not_expr) == "not(@disabled)"

    def test_nested_function_calls(self):
        """Test passing a function call as an argument to another function."""
        nested_expr = F.string_length(F.normalize_space(dot()))
        assert str(nested_expr) == "string-length(normalize-space(.))"

        not_contains_expr = F.not_(F.contains(A.class_, "hidden"))
        assert str(not_contains_expr) == 'not(contains(@class,"hidden"))'

    def test_callable_for_custom_functions(self):
        """
        Test the __call__ method for creating custom function expressions.
        Note: The current implementation requires `name` as a keyword argument.
        """
        # Testing a custom function with one argument
        custom_func_1 = F("some-value", name="my-custom-func")
        assert isinstance(custom_func_1, fun)
        assert str(custom_func_1) == 'my-custom-func("some-value")'

        # Testing a custom function with multiple arguments
        custom_func_2 = F(A.id, 123, name="another-func")
        assert isinstance(custom_func_2, fun)
        assert str(custom_func_2) == "another-func(@id,123)"

        # Testing without arguments
        custom_func_3 = F(name="zero-arg-func")
        assert str(custom_func_3) == "zero-arg-func()"

    @pytest.mark.parametrize("func_name", ["string", "concat", "starts-with", "ends-with", "substring-before", "substring-after", "string-length", "translate", "boolean", "number", "sum", "floor", "ceiling", "round"])
    def test_various_other_functions(self, func_name):
        """A sanity check for a wide range of other function builders."""
        # Hyphenated names are handled correctly by Python's attribute access
        py_func_name = func_name.replace("-", "_")
        func_builder = getattr(F, py_func_name)

        # Test with a simple string argument to ensure it's called correctly
        expr = func_builder("test")
        assert isinstance(expr, fun)
        assert str(expr) == f'{func_name}("test")'
