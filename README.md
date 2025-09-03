# xpath-kit

[![PyPI Version](https://img.shields.io/pypi/v/xpath-kit.svg)](https://pypi.org/project/xpath-kit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/xpath-kit.svg)](https://pypi.org/project/xpath-kit/)

**xpath-kit** is a powerful Python library that provides a fluent, object-oriented, and Pythonic interface for building and executing XPath queries on top of `lxml`. It transforms complex, error-prone XPath string composition into a highly readable and maintainable chain of objects and methods.

Say goodbye to messy, hard-to-read XPath strings:

`div[@id="main" and contains(@class, "content")]/ul/li[position()=1]`

And say hello to a more intuitive and IDE-friendly way of writing queries:

`E.div[(A.id == "main") & A.class_.contains("content")] / E.ul / E.li[1]`

---

## ✨ Features

-   **🐍 Fluent & Pythonic Interface**: Chain methods and operators (`/`, `//`, `[]`, `&`, `|`, `==`, `>`) to build complex XPath expressions naturally using familiar Python logic.
-   **💡 Smart Builders**: Use `E` (elements), `A` (attributes), and `F` (functions) for a highly readable syntax with excellent IDE autocompletion support.
-   **📖 Superb Readability & Maintainability**: Complex queries become self-documenting. It's easier to understand, debug, and modify your selectors.
-   **💪 Powerful Predicate Logic**: Easily create sophisticated predicates for attributes, text, and functions. Gracefully handle multi-class selections with `any()`, `all()`, and `none()`.
-   **🔩 Convenient DOM Manipulation**: The result objects are powerful wrappers around `lxml` elements, allowing for easy DOM traversal and manipulation (e.g., `append`, `remove`, `parent`, `next_sibling`).
-   **🔒 Fully Type-Hinted**: The entire library is fully type-hinted for an unmatched developer experience and static analysis with modern IDEs.
-   **⚙️ HTML & XML Support**: Seamlessly parse both document types with `html()` and `xml()` entry points.

---

## 🚀 Installation

Install `xpath-kit` from PyPI using pip:

```bash
pip install xpath-kit
```

The library requires `lxml` as a dependency, which will be installed automatically.

---

## 🏁 Quick Start

Here's a simple example of how to use `xpath-kit` to parse a piece of HTML and extract information.

```python
from xpathkit import html, E, A, F

html_content = """
<html>
  <body>
    <div id="main">
      <h2>Article Title</h2>
      <p>This is the first paragraph.</p>
      <ul class="item-list">
        <li class="item active">Item 1</li>
        <li class="item">Item 2</li>
        <li class="item disabled">Item 3</li>
      </ul>
    </div>
  </body>
</html>
"""

# 1. Parse the HTML content
root = html(html_content)

# 2. Build a query to find the <li> element with both "item" and "active" classes
# XPath: .//ul[contains(@class, "item-list")]/li[contains(@class, "item") and contains(@class, "active")]
query = E.ul[A.class_.contains("item-list")] / E.li[A.class_.all("item", "active")]

# 3. Execute the query and get a single element
active_item = root.descendant(query)

# Print its content and attributes
print(f"Tag: {active_item.tag}")
print(f"Text: {active_item.string()}")
print(f"Class attribute: {active_item['class']}")

# --- Output ---
# Tag: li
# Text: Item 1
# Class attribute: item active

# 4. Build a more complex query: find all <li> elements whose class does NOT contain 'disabled'
# XPath: .//li[not(contains(@class, "disabled"))]
query_enabled = E.li[F.not_(A.class_.contains("disabled"))]

# 5. Execute the query and process the list of results
enabled_items = root.descendants(query_enabled)
item_texts = enabled_items.map(lambda item: item.string())
print(f"\nEnabled items: {item_texts}")

# --- Output ---
# Enabled items: ['Item 1', 'Item 2']

```

---

## 📚 Core Concepts

### 1. Parsing Entrypoints

Use the `html()` or `xml()` functions to start. They accept a string, bytes, or a file path.

```python
from xpathkit import html, xml

# Parse an HTML string
root_html = html("<div><p>Hello</p></div>")

# Parse an XML file
root_xml = xml(path="data.xml")
```

### 2. The Smart Builders (E, A, F)

These are the heart of `xpath-kit`, making expression building effortless.

-   **`E` (Element)**: Builds element nodes. E.g., `E.div`, `E.a`, or custom tags `E["my-tag"]`.
-   **`A` (Attribute)**: Builds attribute nodes within predicates. E.g., `A.id`, `A.href`, or custom attributes `A["data-id"]`.
-   **`F` (Function)**: Builds XPath functions. E.g., `F.contains()`, `F.not_()`, `F.position()`, or any custom function: `F["name"](arg1, ...)`.

*Note*: Since `class` and `for` are reserved keywords in Python, use a trailing underscore: `A.class_` and `A.for_`.

### 3. Path Selection (`/` and `//`)

Use the division operators to define relationships between elements.

-   `/`: Selects a direct child.
-   `//`: Selects a descendant at any level.

```python
# Selects a <p> that is a direct child of a <div>
# XPath: div/p
query_child = E.div / E.p

# Selects an <a> that is a descendant of the <body>
# XPath: body//a
query_descendant = E.body // E.a
```

You can also use a string directly after an element for simple cases:

```python
# Equivalent to E.div / E.span
query = E.div / "span"
```

This is convenient for simple queries without predicates or attributes.

### 4. Predicates (`[]`)

Use square brackets `[]` on an element to add filtering conditions. This is where `xpath-kit` truly shines.

#### Attribute Predicates with `A`

```python
# Find a div with id="main"
# XPath: //div[@id="main"]
query = E.div[A.id == "main"]

# Find an <a> that has an href attribute
# XPath: //a[@href]
query_has_href = E.a[A.href]

# Find an <li> whose class contains "item" but NOT "disabled"
# XPath: //li[contains(@class,"item") and not(contains(@class,"disabled"))]
query = E.li[A.class_.contains("item") & F.not_(A.class_.contains("disabled"))]
```

#### Text/Value Predicates

To query against the string value of a node (`.`), import the `dot` class.

```python
from xpathkit import dot

# Find an <h1> whose text is exactly "Welcome"
# XPath: //h1[.="Welcome"]
query = E.h1[dot() == "Welcome"]

# Find a <p> whose text contains the word "paragraph"
# XPath: //p[contains(., "paragraph")]
query_contains = E.p[dot().contains("paragraph")]
```

#### Functional Predicates with `F`

Use `F` to call any standard XPath function inside a predicate.

```python
# Select the first list item
# XPath: //li[position()=1]
query_first = E.li[F.position() == 1]

# Select the last list item
# XPath: //li[last()]
query_last = E.li[F.last()]
```

#### Combining Predicates with `&` and `|`

-   `&`: Logical `and`
-   `|`: Logical `or`

```python
# Find an <a> with href="/home" AND a target attribute
# XPath: //a[@href="/home" and @target]
query_and = E.a[(A.href == "/home") & A.target]

# Find a <div> with id="sidebar" OR class="nav"
# XPath: //div[@id="sidebar" or contains(@class,"nav")]
query_or = E.div[(A.id == "sidebar") | A.class_.contains("nav")]
```
**Important:** Due to Python's operator precedence, it's highly recommended to wrap combined conditions in parentheses `()`.

#### Positional Predicates

Use integers (1-based) or negative integers (from the end) directly.

```python
# Select the second <li>
# XPath: //li[2]
query = E.li[2]

# Select the last <li> (equivalent to F.last())
# XPath: //li[last()]
query_last = E.li[-1]
```

### 5. Working with Results

-   `.child()`/`.descendant()` return a single `XPathElement`.
-   `.children()`/`.descendants()` return an `Union[XPathElementList, str, float, bool, List[str]]`.

#### `XPathElement` (Single Result)

-   `.tag`: The element's tag name (e.g., `'div'`).
-   `.attr`: A dictionary of all attributes.
-   `element['name']`: Access an attribute directly.
-   `.string()`: Get the concatenated text of the element and all its children (`string(.)`).
-   `.text()`: Get a list of only the element's direct text nodes (`./text()`).
-   `.parent()`: Get the parent element.
-   `.next_sibling()` / `.prev_sibling()`: Get adjacent sibling elements.
-   `.xpath(query)`: Execute a raw string or a constructed query within the context of this element.

#### `XPathElementList` (Multiple Results)

-   `.one()`: Ensures the list contains exactly one element and returns it; otherwise, raises an error.
-   `.first()` / `.last()`: Get the first or last element; raises an error if the list is empty.
-   `len(element_list)`: Get the number of elements.
-   `.filter(func)`: Filter the list based on a function.
-   `.map(func)`: Apply a function to each element and return a list of the results.
-   Can be iterated over directly: `for e in my_list: ...`
-   Supports slicing and indexing: `my_list[0]`, `my_list[-1]`

### 6. DOM Manipulation

Modify the document tree with ease.

```python
from xpathkit import XPathElement, E, A

# Assuming 'root' is a parsed XPathElement
# Find the <ul> element
ul = root.descendant(E.ul)

# Create and append a new <li>
new_li = XPathElement.create("li", attr={"class": "new-item"}, text="Item 4")
ul.append(new_li)

# Remove an element
item_to_remove = ul.child(E.li[A.class_.contains("disabled")])
if item_to_remove:
    ul.remove(item_to_remove)

# Print the modified HTML
print(root.tostring())
```

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.