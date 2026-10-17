# Maths

Mathematical notation can be rendered in three ways. Only the `markdown_katex`
route runs at build time; the other two execute JavaScript in a headless Chrome
(`render_js: true`).

## KaTeX (markdown_katex)

[KaTeX] rendered by the [`markdown_katex`][markdown-katex] extension. KaTeX runs
during the Markdown build, so the result is baked into the combined HTML and
rendered into the PDF by WeasyPrint as **selectable text and MathML**.

``` yaml
markdown_extensions:
  - markdown_katex:
      no_inline_svg: true  # required for WeasyPrint
      insert_fonts_css: true
```

### Inline

Inline formulas use `` $`...`$ ``:

The solutions of a quadratic equation are given by
$`x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}`$.

### Display

Display formulas use a fenced `math` block:

```math
f(x) = \int_{-\infty}^{\infty} \hat f(\xi)\,e^{2 \pi i \xi x} \,d\xi
```

#### Fractions

```math
\frac{1}{\left(\sqrt{\phi \sqrt{5}} - \phi\right) e^{\frac{2}{5} \pi}}
= 1 + \cfrac{e^{-2\pi}}{1 + \cfrac{e^{-4\pi}}{1 + \cfrac{e^{-6\pi}}{1 + \cdots}}}
```

#### Matrices

```math
\begin{pmatrix}
a & b \\
c & d
\end{pmatrix}
\begin{pmatrix}
x \\
y
\end{pmatrix}
=
\begin{pmatrix}
ax + by \\
cx + dy
\end{pmatrix}
```

#### Aligned equations

```math
\begin{aligned}
\nabla \cdot \vec{E} &= \frac{\rho}{\varepsilon_0} \\
\nabla \cdot \vec{B} &= 0 \\
\nabla \times \vec{E} &= -\frac{\partial \vec{B}}{\partial t}
\end{aligned}
```

## KaTeX (chromium)

KaTeX can also be rendered in the browser by executing JavaScript in a headless
Chrome. Use [`pymdownx.arithmatex`][arithmatex] for the delimiters and add the
[KaTeX auto-render][katex-auto-render] scripts.

``` yaml
markdown_extensions:
  - pymdownx.arithmatex:
      generic: true
      tex_inline_wrap: ["$", "$"]
      tex_block_wrap: ["$$", "$$"]

plugins:
  - to-pdf:
      render_js: true
      headless_chrome_path: chromium

extra_javascript:
  - javascripts/katex.js
  - https://unpkg.com/katex@0/dist/katex.min.js
  - https://unpkg.com/katex@0/dist/contrib/auto-render.min.js

extra_css:
  - https://unpkg.com/katex@0/dist/katex.min.css
```

``` js title="docs/javascripts/katex.js"
window.addEventListener("DOMContentLoaded", function () {
  renderMathInElement(document.body, {
    delimiters: [
      { left: "$$", right: "$$", display: true },
      { left: "$", right: "$", display: false },
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true }
    ]
  });
});
```

## MathJax (chromium)

[MathJax] renders in the browser, so the PDF must be built with
`render_js: true` and a headless Chrome available.

``` yaml
markdown_extensions:
  - pymdownx.arithmatex:
      generic: true

plugins:
  - to-pdf:
      render_js: true
      headless_chrome_path: chromium

extra_javascript:
  - javascripts/mathjax.js
  - https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js
```

``` js title="docs/javascripts/mathjax.js"
window.MathJax = {
  tex: {
    inlineMath: [["$", "$"], ["\\(", "\\)"]],
    displayMath: [["$$", "$$"], ["\\[", "\\]"]]
  }
};
```

Inline and display formulas are then written between single and double dollar
delimiters respectively.

[KaTeX]: https://katex.org/
[katex-auto-render]: https://katex.org/docs/autorender.html
[markdown-katex]: https://github.com/mbarkhau/markdown-katex
[MathJax]: https://www.mathjax.org/
[arithmatex]: https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/
