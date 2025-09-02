import pytest

from xpathkit.builders import A, E, F
from xpathkit.expressions import attr, dot, ele, fun


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
def test_common_element_properties(prop_name, expected_tag):
    element_expr = getattr(E, prop_name)
    assert isinstance(element_expr, ele)
    assert str(element_expr) == expected_tag


@pytest.mark.parametrize(
    "special,expected",
    [
        ("any", "*"),
        ("parent", ".."),
        ("root", "."),
    ],
)
def test_special_element_properties(special, expected):
    el = getattr(E, special)
    assert isinstance(el, ele)
    assert str(el) == expected


@pytest.mark.parametrize(
    "custom,expected",
    [
        ("my-custom-element", "my-custom-element"),
        ("svg:path", "svg:path"),
    ],
)
def test_callable_for_custom_tags(custom, expected):
    custom_el = E(custom)
    assert isinstance(custom_el, ele)
    assert str(custom_el) == expected


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
def test_common_attribute_properties(prop_name, expected_attr):
    attr_expr = getattr(A, prop_name)
    assert isinstance(attr_expr, attr)
    assert attr_expr.part() == expected_attr


@pytest.mark.parametrize(
    "kw,expected",
    [
        ("class_", "@class"),
        ("for_", "@for"),
    ],
)
def test_keyword_attribute_properties(kw, expected):
    attr_obj = getattr(A, kw)
    assert isinstance(attr_obj, attr)
    assert str(attr_obj) == expected


@pytest.mark.parametrize(
    "custom,expected",
    [
        ("data-testid", "@data-testid"),
        ("xml:lang", "@xml:lang"),
    ],
)
def test_callable_for_custom_attributes(custom, expected):
    custom_attr = A(custom)
    assert isinstance(custom_attr, attr)
    assert str(custom_attr) == expected


@pytest.mark.parametrize(
    "func,expected",
    [
        (F.position(), "position()"),
        (F.last(), "last()"),
        (F.true(), "true()"),
        (F.false(), "false()"),
    ],
)
def test_functions_with_no_args(func, expected):
    assert isinstance(func, fun)
    assert str(func) == expected


def test_functions_with_one_arg():
    count_expr = F.count(A.id)
    assert isinstance(count_expr, fun)
    assert str(count_expr) == "count(@id)"

    norm_space_expr = F.normalize_space(dot())
    assert isinstance(norm_space_expr, fun)
    assert str(norm_space_expr) == "normalize-space(.)"

    lang_expr = F.lang("en")
    assert str(lang_expr) == 'lang("en")'


def test_functions_with_multiple_args():
    contains_expr = F.contains(A.class_, "item")
    assert str(contains_expr) == 'contains(@class,"item")'

    substring_expr = F.substring("hello world", 1, 5)
    assert str(substring_expr) == 'substring("hello world",1,5)'

    concat_expr = F.concat("a", "b", "c")
    assert str(concat_expr) == 'concat("a","b","c")'


@pytest.mark.parametrize(
    "arg,expected",
    [
        (A.disabled, "not(@disabled)"),
        (F.contains(A.class_, "hidden"), 'not(contains(@class,"hidden"))'),
    ],
)
def test_not_function_handling(arg, expected):
    not_expr = F.not_(arg)
    assert isinstance(not_expr, fun)
    assert str(not_expr) == expected


def test_nested_function_calls():
    nested_expr = F.string_length(F.normalize_space(dot()))
    assert str(nested_expr) == "string-length(normalize-space(.))"


@pytest.mark.parametrize(
    "args,name,expected",
    [
        (("some-value",), "my-custom-func", 'my-custom-func("some-value")'),
        ((A.id, 123), "another-func", "another-func(@id,123)"),
        ((), "zero-arg-func", "zero-arg-func()"),
    ],
)
def test_callable_for_custom_functions(args, name, expected):
    custom_func = F(*args, name=name)
    assert isinstance(custom_func, fun)
    assert str(custom_func) == expected


@pytest.mark.parametrize(
    "func_name",
    [
        "string",
        "concat",
        "starts-with",
        "ends-with",
        "substring-before",
        "substring-after",
        "string-length",
        "translate",
        "boolean",
        "number",
        "sum",
        "floor",
        "ceiling",
        "round",
    ],
)
def test_various_other_functions(func_name):
    py_func_name = func_name.replace("-", "_")
    func_builder = getattr(F, py_func_name)
    expr = func_builder("test")
    assert isinstance(expr, fun)
    assert str(expr) == f'{func_name}("test")'
