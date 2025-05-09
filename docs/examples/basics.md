# Basics

From [original Markdown](https://daringfireball.net/projects/markdown/basics) syntax

## Paragraphs, Headers, and Block Quotes

### A Third Level Header

Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.

The quick brown fox jumped over the lazy
dog's back.

#### Header 4

> This is a block quote.
>
> This is the second paragraph in the block quote.
>
> ## This is an H2 in a block quote

## Phrase Emphasis

Some of these words *are emphasized*.
Some of these words _are emphasized also_.

Use two asterisks for **strong emphasis**.
Or, if you prefer, __use two underscores instead__.

## Lists

### Using `*`

*   Candy.
*   Gum.
*   Booze.

### Using `+`

+   Candy.
+   Gum.
+   Booze.

### Using `-`

-   Candy.
-   Gum.
-   Booze.

### Ordered list

1.  Red
2.  Green
3.  Blue

### `<p>` tags for the list

*   A list item.

    With multiple paragraphs.

*   Another item in the list.

## Links

This is an [example link](http://example.com/).

I get 10 times more traffic from [Google][1] than from
[Yahoo][2] or [MSN][3].

[1]: http://google.com/        "Google"
[2]: http://search.yahoo.com/  "Yahoo Search"
[3]: http://search.msn.com/    "MSN Search"

## Images

![alt text](https://dummyimage.com/600x400/ "Title")

## Code

I strongly recommend against using any `<blink>` tags.

I wish SmartyPants used named entities like `&mdash;`
instead of decimal-encoded entities like `&#8212;`.

If you want your page to validate under XHTML 1.0 Strict,
you've got to put paragraph tags in your block quotes:

    <blockquote>
        <p>For example.</p>
    </blockquote>
