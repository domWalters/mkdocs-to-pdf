# Grids and Admonitions

Material uses CSS grid for cards; WeasyPrint has regressed on grid layout
before.

## Grid cards

<div class="grid cards" markdown>

-   __Set up in 5 minutes__

    ---

    Install with `pip` and get up and running in minutes.

-   __It's just Markdown__

    ---

    Focus on your content and generate a responsive static site.

-   __Made to measure__

    ---

    Change the colors, fonts, language and icons with a few lines.

-   __Open Source, MIT__

    ---

    Licensed under MIT and available on GitHub.

</div>

## Admonitions

!!! note

    A note admonition.

!!! abstract

    An abstract admonition.

!!! info

    An info admonition.

!!! tip

    A tip admonition.

!!! success

    A success admonition.

!!! question

    A question admonition.

!!! warning

    A warning admonition.

!!! failure

    A failure admonition.

!!! danger

    A danger admonition.

!!! bug

    A bug admonition.

!!! example

    An example admonition.

!!! quote

    A quote admonition.

??? note

    A collapsible admonition.

    ```python
    print("WEASYPRINT_ADMONITION_SENTINEL")
    ```

## Content tabs

=== "Tab one"

    Tab one content.

=== "Tab two"

    Tab two content.

| Column A | Column B |
| -------- | -------- |
| A1       | B1       |
| A2       | B2       |

A footnote reference.[^1]

[^1]: WEASYPRINT_FOOTNOTE_SENTINEL

## Grid Sentinel Heading

WEASYPRINT_GRID_SENTINEL
