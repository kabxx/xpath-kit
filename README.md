# xpathkit

[![PyPI Version](https://img.shields.io/pypi/v/xpathkit.svg)](https://pypi.org/project/xpathkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/xpathkit.svg)](https://pypi.org/project/xpathkit/)

**xpathkit** is a Python library that provides a fluent, object-oriented, and Pythonic interface for building and executing XPath queries on top of `lxml`. It transforms complex XPath string composition into a readable and maintainable chain of objects and methods.

Say goodbye to messy, hard-to-read XPath strings:

`//div[@id="main" and contains(@class, "content")]/ul/li[position()=1]`

And say hello to a more intuitive way of writing queries:

`ele("div")[(attr("id") == "main") & (attr("class").any("content")] / "ul" / ele("li")[0]`

---

## Features

-   **✨ Fluent Interface**: Chain methods and operators (`/`, `//`, `[]`, `&`, `|`) to build complex XPath expressions naturally.
-   **🐍 Pythonic**: Write XPath using familiar Python objects, operators, and logic. No more escaping quotes or manual string concatenation.
-   **📖 Readability & Maintainability**: Complex queries become self-documenting. It's easier to understand, debug, and modify your selectors.
-   **💪 Powerful Selection**: Easily create sophisticated predicates for attributes, including checking for multiple class names (`any`, `all`, `none`).
-   ** DOM Manipulation**: The result objects are powerful wrappers around `lxml` elements, allowing for easy DOM traversal and manipulation (e.g., `append`, `remove`, `parent`).
-   **🔒 Type-Hinted**: The entire library is fully type-hinted for a better development experience with modern IDEs.

---

## Installation

Install `xpathkit` from PyPI using pip:

```bash
pip install xpathkit
```

The library requires `lxml` as a dependency, which will be installed automatically.

---

## Quick Start

Here's a simple example of how to use `xpathkit` to parse a piece of HTML and extract information.

```python
from xpathkit import xpath, ele, attr

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

# Parse the HTML content
root = xpath(html_content)

# Build a query to find the active list item
# This translates to: .//ul[contains(@class, "item-list")]/li[contains(@class, "active")]
query = ele("ul")[attr("class").any("item-list")] / ele("li")[attr("class").any("active")]

# Execute the query and get a single element
active_item = root.descendant(query)

# Print its content and attributes
print(f"Tag: {active_item.tag}")
print(f"Text: {active_item.string()}")
print(f"Class attribute: {active_item['class']}")

# --- Output ---
# Tag: li
# Text: Item 1
# Class attribute: item active
```

---

## Core Concepts

### 1. Parsing and Entrypoint

The `xpath()` function is the main entry point. It takes a string or bytes of HTML/XML content and returns the root `XPathElement`.

```python
from xpathkit import xpath

root = xpath("<p>Hello</p>")
```

### 2. Building Expressions with `ele` and `attr`

-   **`ele(name)`**: Represents an element node (e.g., `div`, `a`, `p`).
-   **`attr(name)`**: Represents an attribute within a predicate (e.g., `id`, `class`, `href`).

### 3. Path Selection (`/` and `//`)

Use the division operators to define relationships between elements.

-   **`/` (`__truediv__`)**: Selects a direct child.
-   **`//` (`__floordiv__`)**: Selects a descendant at any level.

```python
# Selects a <p> that is a direct child of a <div>
query_child = ele("div") / "p"  # You can use strings for simplicity

# Selects an <a> that is a descendant of the <body>
query_descendant = ele("body") // ele("a")
```

### 4. Predicates (`[]`)

Use square brackets (`__getitem__`) on an `ele` object to add conditions (predicates).

#### Attribute Predicates with `attr`

```python
# Find an input with name="username"
# Equivalent to: //input[@name="username"]
query = ele("input")[attr("name") == "username"]

# Find an element with a specific class
# Equivalent to: //div[contains(@class, "widget")]
query = ele("div")[attr("class").any("widget")]

# Find an element that has ALL of the given classes
# Equivalent to: //li[contains(@class, "item") and contains(@class, "active")]
query = ele("li")[attr("class").all("item", "active")]

# Find an element that does NOT contain any of the given classes
# Equivalent to: //button[not(contains(@class, "disabled")) and not(contains(@class, "hidden"))]
query = ele("button")[attr("class").none("disabled", "hidden")]
```

#### Combining Predicates with `&` and `|`

-   **`&` (`__and__`)**: Logical `and`.
-   **`|` (`__or__`)**: Logical `or`.

```python
# Find a link that has a specific href AND a target attribute
# //a[@href="/home" and @target]
query_and = ele("a")[ (attr("href") == "/home") & attr("target") ]

# Find an element with id="sidebar" OR class="nav"
# //div[@id="sidebar" or contains(@class,"nav")]
query_or = ele("div")[ (attr("id") == "sidebar") | attr("class").any("nav") ]
```
**Note:** Due to Python's operator precedence, it's recommended to wrap conditions in parentheses `()` when combining them.

#### Positional Predicates

You can also use numbers directly to specify position.

```python
# Select the second list item
# //ul/li[2]
query = ele("ul") / ele("li")[2]
```

### 5. Working with Results

Queries return either an `XPathElement` (for `.child()`/`.descendant()`) or an `XPathElementList` (for `.children()`/`.descendants()`).

#### `XPathElement` (Single Result)

-   `.tag`: The element's tag name (e.g., `'div'`).
-   `.attr`: A dictionary of attributes.
-   `element['name']`: Access an attribute directly.
-   `.string()`: Get all concatenated text from the element and its children.
-   `.text()`: Get only the direct text nodes of the element.
-   `.parent()`: Get the parent element.

#### `XPathElementList` (Multiple Results)

-   `.one()`: Returns the single element in the list. Raises an error if the list doesn't contain exactly one element.
-   `.first()` / `.last()`: Get the first or last element.
-   `len()`: Get the number of elements.
-   `.filter(func)`: Filter the list based on a function.
-   `.map(func)`: Apply a function to each element and return a list of results.
-   `for e in element_list.to_list()`: Iterate through the elements.

```python
links = root.descendants(ele("a"))

# Map to get all hrefs
hrefs = links.map(lambda link: link["href"])

# Filter for external links
external_links = links.filter(lambda link: link["href"].startswith("http"))
```

### 6. DOM Manipulation

`XPathElement` provides methods to modify the XML/HTML tree.

```python
from xpathkit import XPathElement

# Find an element
ul = root.descendant(ele("ul"))

# Create a new element
new_li = XPathElement.create("li", attr={"class": "new-item"}, text="Item 4")

# Append it
ul.append(new_li)

# Remove an element
item_to_remove = ul.child(ele("li")[attr("class").any("disabled")])
ul.remove(item_to_remove)

print(root.tostring()) # See the modified HTML
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.