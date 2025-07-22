# FAQ

## My PDF is just a web error message

This can happen if you have used [`chromium`][chromium] installed using
[`snap`][snap] to render the PDF.

!!! tip

    If you are using a modern version of Ubuntu, approximately 23.10 or newer,
    this will apply to you.

Programs installed using [`snap`][snap] do not have rootless access to `/tmp`
which this plugin uses.

Current workaround until this is addressed is to download [`chromium`][chromium]
directly without [`snap`][snap], and specify the executable with
[`headless_chrome_path`][config-headless-chrome-path].


[chromium]: https://www.chromium.org/getting-involved/download-chromium/
[config-headless-chrome-path]: ./usage.md#`headless_chrome_path` (only if `pdf_engine: chromium`)
[snap]: https://snapcraft.io/about
