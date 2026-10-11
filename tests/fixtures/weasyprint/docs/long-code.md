# Long Code

A code block with line numbers that is longer than a single page. WeasyPrint
has historically dropped everything after such a block (see issue #62).

```python linenums="1"
"""A deliberately long module used to force a page break inside a code block."""

import logging
import pathlib
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import ClassVar

logger = logging.getLogger(__name__)


@dataclass
class Node:
    """A single node in the graph."""

    name: str
    weight: int = 0
    children: list["Node"] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)

    registry: ClassVar[dict[str, "Node"]] = {}

    def add_child(self, child: "Node") -> None:
        """Append a child and record it in the registry."""
        self.children.append(child)
        self.registry[child.name] = child

    def total_weight(self) -> int:
        """Return the weight of this node and all descendants."""
        return self.weight + sum(child.total_weight() for child in self.children)

    def leaves(self) -> Iterable["Node"]:
        """Yield every leaf node reachable from this node."""
        if not self.children:
            yield self
        for child in self.children:
            yield from child.leaves()


def parse_line(line: str) -> tuple[str, int] | None:
    """Parse a `name weight` line, returning None for comments and blanks."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    match = re.match(r"^(?P<name>[\w.-]+)(?:\s+(?P<weight>\d+))?$", stripped)
    if match is None:
        raise ValueError(f"cannot parse line: {stripped!r}")
    name = match.group("name")
    weight = int(match.group("weight") or 0)
    return name, weight


def build_tree(lines: Iterable[str]) -> Node:
    """Build a forest root from indentation-free `name weight` lines."""
    root = Node("root")
    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            continue
        name, weight = parsed
        root.add_child(Node(name=name, weight=weight))
    return root


def walk(node: Node, visit: Callable[[Node], None]) -> None:
    """Depth-first traversal applying `visit` to every node."""
    visit(node)
    for child in node.children:
        walk(child, visit)


def summarize(node: Node) -> dict[str, int]:
    """Return a summary of node names and weights."""
    summary: dict[str, int] = {}

    def record(current: Node) -> None:
        summary[current.name] = current.total_weight()

    walk(node, record)
    return summary


def write_report(path: pathlib.Path, node: Node) -> None:
    """Write a plain-text report for the given tree."""
    summary = summarize(node)
    lines = [f"{name}: {weight}" for name, weight in sorted(summary.items())]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("wrote %d entries to %s", len(lines), path)


def load(path: pathlib.Path) -> Node:
    """Load a tree from a text file."""
    return build_tree(path.read_text(encoding="utf-8").splitlines())


def main() -> None:
    """Load a tree, summarize it and write a report."""
    import sys

    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) != 2:
        raise SystemExit("usage: long_code.py <path>")
    tree = load(pathlib.Path(sys.argv[1]))
    write_report(pathlib.Path("report.txt"), tree)
    for leaf in tree.leaves():
        print(leaf.name, leaf.total_weight())


WEASYPRINT_CODE_SENTINEL = "the end of a very long code block"
```
