# GLightbox image links

`mkdocs-glightbox` wraps every image in an anchor that points back at the
image. That relative href cannot be resolved in the combined PDF, so the
anchor is dropped while the image is kept.

<a class="glightbox" href="./assets/image.svg"><img alt="Linked image" src="./assets/image.svg"></a>

A plain image is left untouched:

![Plain image](./assets/image.svg)
