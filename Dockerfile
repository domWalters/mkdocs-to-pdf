FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

RUN \
    apk update \
    && apk add --update --upgrade --no-cache \
        cairo-dev fontconfig font-noto g++ gcc gdk-pixbuf-dev libsass make \
        musl-dev pango-dev podman-compose uv \
    && fc-cache -f

RUN \
    addgroup -g 1000 -S mkdocs \
    && adduser -u 1000 -S mkdocs -G mkdocs
USER mkdocs

WORKDIR /mkdocs
COPY --chown=mkdocs:mkdocs pyproject.toml .
COPY --chown=mkdocs:mkdocs Makefile .

RUN touch README.md && make sync

COPY --chown=mkdocs:mkdocs custom_style_src ./custom_style_src
COPY --chown=mkdocs:mkdocs docs ./docs
COPY --chown=mkdocs:mkdocs src ./src
COPY --chown=mkdocs:mkdocs CHANGELOG .
COPY --chown=mkdocs:mkdocs LICENSE .
COPY --chown=mkdocs:mkdocs docker-compose.yml .
COPY --chown=mkdocs:mkdocs mkdocs.yml .

RUN ls && make docs
