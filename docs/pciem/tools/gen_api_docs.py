#!/usr/bin/env python3
"""
gen_api_docs.py — PCIem API documentation generator
=====================================================

Parses one or more C header files and emits a structured mdbook Markdown page,
or a JSON AST dump for downstream tooling.

Usage
-----
    python3 gen_api_docs.py [options] header.h [header2.h ...]

Options
-------
    -o FILE              Output file (default: stdout)
    -t TITLE             Page title (default: "API Reference")
    -v VERSION           Doc version string written into <meta> tag
    --desc FILE          TOML overlay with hand-written descriptions
    --ioctl-prefix PFX   Prefix that identifies IOCTL #defines (default: PCIEM_IOCTL_)
    --exclude-prefix PFX Ignore structs/defines whose names start with PFX (repeatable)
    --toc                Emit a table of contents
    --no-meta            Skip the version <meta> tag
    --json               Dump parsed AST as JSON instead of Markdown
    --check              Compare rendered output against -o FILE; exit 1 if different
    --warn-undoc         Print warnings for items that have no description
    --self-test          Run built-in unit tests and exit

What it extracts from headers
------------------------------
  * /** ... */ or /// doc-comments immediately before a definition
  * Doc-comment tags:  @param, @note, @deprecated, @since, @returns
  * Multi-line #define (backslash-continued lines are joined)
  * struct / union definitions -> fenced code block + field table
  * #define constant groups -> grouped tables (smart prefix merging)
  * #define PCIEM_IOCTL_* -> IOCTL sections with cross-links
  * __attribute__((packed)) / aligned is stripped cleanly
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict, OrderedDict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@dataclass
class DocTags:
    """Structured tags extracted from a /** */ or /// doc comment."""
    params:     Dict[str, str] = field(default_factory=dict)
    note:       str = ""
    deprecated: str = ""
    since:      str = ""
    returns:    str = ""
    body:       str = ""


@dataclass
class StructField:
    type_str:     str
    name:         str
    array_suffix: str = ""
    comment:      str = ""


@dataclass
class StructDef:
    name:        str
    kind:        str = "struct"
    fields:      List[StructField] = field(default_factory=list)
    doc:         DocTags = field(default_factory=DocTags)
    source_file: str = ""
    line:        int = 0


@dataclass
class Define:
    name:        str
    value:       str
    doc:         DocTags = field(default_factory=DocTags)
    source_file: str = ""
    line:        int = 0


@dataclass
class IoctlDef:
    name:        str
    macro:       str
    magic:       str
    number:      str
    struct_name: str
    doc:         DocTags = field(default_factory=DocTags)
    source_file: str = ""
    line:        int = 0


@dataclass
class ParseResult:
    structs:  List[StructDef]  = field(default_factory=list)
    defines:  List[Define]     = field(default_factory=list)
    ioctls:   List[IoctlDef]   = field(default_factory=list)
    warnings: List[str]        = field(default_factory=list)

_TAG_RE = re.compile(
    r'@(param|note|deprecated|since|returns?)\s*'
    r'(?:(\w+)\s+)?'
    r'(.*?)(?=@\w|\Z)',
    re.DOTALL,
)


def _parse_doc_tags(raw: str) -> DocTags:
    """Parse a raw doc-comment string into a DocTags instance."""
    cleaned = '\n'.join(
        ln.strip().lstrip('*').strip() for ln in raw.splitlines()
    ).strip()

    tags = DocTags()
    body_parts: List[str] = []
    last_end = 0

    for m in _TAG_RE.finditer(cleaned):
        if m.start() > last_end:
            body_parts.append(cleaned[last_end:m.start()].strip())
        last_end = m.end()

        tag   = m.group(1).lower()
        name  = m.group(2) or ""
        value = m.group(3).strip().replace('\n', ' ')

        if tag == 'param' and name:
            tags.params[name] = value
        elif tag == 'note':
            tags.note = value
        elif tag == 'deprecated':
            tags.deprecated = value
        elif tag == 'since':
            tags.since = value
        elif tag in ('returns', 'return'):
            tags.returns = value

    if last_end < len(cleaned):
        body_parts.append(cleaned[last_end:].strip())

    tags.body = '\n\n'.join(p for p in body_parts if p)
    return tags


def _inline_comment(line: str) -> Tuple[str, str]:
    """Strip trailing /* … */ or // comment; return (clean_line, comment)."""
    m = re.search(r'/\*\*?\s*(.*?)\s*\*/', line)
    if m:
        return line[:m.start()].rstrip(), m.group(1).strip()
    m = re.search(r'//+\s*(.*)', line)
    if m:
        return line[:m.start()].rstrip(), m.group(1).strip()
    return line, ""

def _join_continuations(lines: List[str]) -> List[Tuple[int, str]]:
    """Return (original_1based_lineno, joined_line) pairs."""
    out: List[Tuple[int, str]] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        lineno = i + 1
        if ln.rstrip().endswith('\\'):
            parts = [ln.rstrip()[:-1]]
            while ln.rstrip().endswith('\\') and i + 1 < len(lines):
                i += 1
                ln = lines[i]
                parts.append(ln.rstrip().rstrip('\\'))
            out.append((lineno, ' '.join(p.strip() for p in parts)))
        else:
            out.append((lineno, ln))
        i += 1
    return out

_ATTR_RE       = re.compile(r'__attribute__\s*\(\s*\(.*?\)\s*\)', re.DOTALL)
_DEFINE_RE     = re.compile(r'#\s*define\s+(\w+)\s+(.*)')
_STRUCT_RE     = re.compile(r'\b(struct|union)\s+(\w+)\s*\{?')
_FIELD_RE      = re.compile(
    r'^\s*'
    r'((?:const\s+|volatile\s+|unsigned\s+|signed\s+|__percpu\s+)*'
    r'(?:struct\s+\w+|union\s+\w+|enum\s+\w+|\w+))'
    r'\s*(\*+)?'
    r'\s*(\w+)'
    r'(\[.*?\])?'
    r'\s*;'
)

_NOISE_RE      = re.compile(r'^(_[A-Z_]+_H_?$|pr_fmt$|KBUILD_MODNAME$)')


def _strip_attrs(s: str) -> str:
    return _ATTR_RE.sub('', s).strip()


def _make_ioctl_re(prefix: str) -> re.Pattern:
    p = re.escape(prefix)
    return re.compile(
        rf'#\s*define\s+({p}\w+)\s+'
        r'(_IO(?:WR?|R)?)\s*\(\s*(\w+)\s*,\s*(\d+)'
        r'(?:\s*,\s*struct\s+(\w+))?\s*\)'
    )

def _parse_file(path: str, ioctl_re: re.Pattern,
                exclude_prefixes: List[str]) -> ParseResult:
    result = ParseResult()
    source = Path(path).name

    try:
        text = Path(path).read_text(errors='replace')
    except FileNotFoundError:
        result.warnings.append(f"{path}: file not found, skipping")
        return result

    lines = _join_continuations(text.splitlines())
    pending_doc: Optional[str] = None
    i = 0

    def _skip(name: str) -> bool:
        return any(name.startswith(p) for p in exclude_prefixes)

    while i < len(lines):
        lineno, line = lines[i]
        stripped = line.strip()

        if stripped.startswith('/**'):
            block = stripped
            while '*/' not in block and i + 1 < len(lines):
                i += 1
                block += '\n' + lines[i][1].strip()
            m = re.search(r'/\*\*(.*?)\*/', block, re.DOTALL)
            pending_doc = m.group(1) if m else ""
            i += 1
            continue

        if stripped.startswith('///'):
            doc_lines = [stripped[3:].strip()]
            while i + 1 < len(lines) and lines[i + 1][1].strip().startswith('///'):
                i += 1
                doc_lines.append(lines[i][1].strip()[3:].strip())
            pending_doc = '\n'.join(doc_lines)
            i += 1
            continue

        if stripped.startswith('/*'):
            while '*/' not in line and i + 1 < len(lines):
                i += 1
                _, line = lines[i]
            pending_doc = None
            i += 1
            continue

        if stripped.startswith('//'):
            pending_doc = None
            i += 1
            continue

        m = ioctl_re.match(stripped)
        if m:
            name = m.group(1)
            if not _skip(name):
                doc = _parse_doc_tags(pending_doc) if pending_doc is not None else DocTags()
                result.ioctls.append(IoctlDef(
                    name=name, macro=m.group(2), magic=m.group(3),
                    number=m.group(4), struct_name=m.group(5) or "",
                    doc=doc, source_file=source, line=lineno,
                ))
            pending_doc = None
            i += 1
            continue

        m = _DEFINE_RE.match(stripped)
        if m:
            name = m.group(1)
            value_raw = m.group(2).strip()
            value, inline_cmt = _inline_comment(value_raw)
            value = _strip_attrs(value.strip())

            if not _NOISE_RE.match(name) and not _skip(name):
                doc_raw = pending_doc if pending_doc is not None else (inline_cmt or "")
                doc = _parse_doc_tags(doc_raw)
                if not doc.body and inline_cmt:
                    doc.body = inline_cmt
                result.defines.append(Define(
                    name=name, value=value, doc=doc,
                    source_file=source, line=lineno,
                ))
            pending_doc = None
            i += 1
            continue

        m = _STRUCT_RE.search(stripped)
        if m:
            kind  = m.group(1)
            sname = m.group(2)

            has_brace = '{' in stripped
            if not has_brace:
                j = i + 1
                while j < len(lines) and not lines[j][1].strip():
                    j += 1
                if j < len(lines) and lines[j][1].strip().startswith('{'):
                    has_brace = True
                    i = j
                else:
                    pending_doc = None
                    i += 1
                    continue

            doc   = _parse_doc_tags(pending_doc) if pending_doc is not None else DocTags()
            pending_doc = None

            sdef  = StructDef(name=sname, kind=kind, doc=doc,
                              source_file=source, line=lineno)

            depth = stripped.count('{') - stripped.count('}')
            if depth == 0 and has_brace:
                depth = 1
            i += 1

            while i < len(lines) and depth > 0:
                _, ln = lines[i]
                raw_field, inline_cmt = _inline_comment(ln)
                raw_field = _strip_attrs(raw_field)
                depth += raw_field.count('{') - raw_field.count('}')

                if depth > 0:
                    fm = _FIELD_RE.match(raw_field)
                    if fm:
                        base   = fm.group(1).strip()
                        stars  = (fm.group(2) or "").strip()
                        fname  = fm.group(3)
                        arr    = (fm.group(4) or "").strip()
                        fdoc   = sdef.doc.params.get(fname, "") or inline_cmt
                        sdef.fields.append(StructField(
                            type_str=base + (' ' + stars if stars else ''),
                            name=fname, array_suffix=arr, comment=fdoc,
                        ))
                i += 1

            if not _skip(sname):
                result.structs.append(sdef)
            continue

        if stripped and not stripped.startswith('#'):
            pending_doc = None

        i += 1

    return result

def _merge(results: List[ParseResult]) -> ParseResult:
    """Merge multiple ParseResults; first definition of each name wins."""
    combined = ParseResult()
    seen_s: Set[str] = set()
    seen_d: Set[str] = set()
    seen_i: Set[str] = set()

    for r in results:
        combined.warnings.extend(r.warnings)
        for s in r.structs:
            if s.name not in seen_s:
                seen_s.add(s.name)
                combined.structs.append(s)
        for d in r.defines:
            if d.name not in seen_d:
                seen_d.add(d.name)
                combined.defines.append(d)
        for io in r.ioctls:
            if io.name not in seen_i:
                seen_i.add(io.name)
                combined.ioctls.append(io)

    return combined

def _load_overlay(path: Optional[str]) -> dict:
    if not path or not os.path.exists(path):
        return {}
    if tomllib is None:
        print("[warn] tomllib/tomli not available; --desc overlay ignored.", file=sys.stderr)
        return {}
    with open(path, 'rb') as f:
        return tomllib.load(f)


def _ov(overlay: dict, *keys: str) -> dict:
    """Safely drill into nested overlay keys; return {} on any miss."""
    node = overlay
    for k in keys:
        node = node.get(k, {})
        if not isinstance(node, dict):
            return {}
    return node

def _warn_undocumented(result: ParseResult, overlay: dict) -> List[str]:
    out = []
    for s in result.structs:
        ov = _ov(overlay, 'structs', s.name)
        if not s.doc.body and not ov.get('description'):
            out.append(f"struct {s.name} ({s.source_file}:{s.line}): no description")
        for f in s.fields:
            ov_f = _ov(overlay, 'structs', s.name, 'fields', f.name)
            if not f.comment and not ov_f.get('description') and not s.doc.params.get(f.name):
                out.append(f"  struct {s.name}.{f.name}: no field description")
    for io in result.ioctls:
        ov = _ov(overlay, 'ioctls', io.name)
        if not io.doc.body and not ov.get('description'):
            out.append(f"ioctl {io.name} ({io.source_file}:{io.line}): no description")
    return out


def _to_json(result: ParseResult) -> str:
    return json.dumps(asdict(result), indent=2)

def _anchor(name: str)        -> str: return name.lower().replace('_', '-')
def _struct_anchor(name: str) -> str: return f"struct-{_anchor(name)}"
def _ioctl_anchor(name: str)  -> str: return f"ioctl-{_anchor(name)}"

def _render_doc_tags(tags: DocTags, extra: str = "") -> List[str]:
    out = []
    body = extra or tags.body
    if body:
        out.append(body + "\n")
    if tags.deprecated:
        out.append(f"> **Deprecated:** {tags.deprecated}\n")
    if tags.since:
        out.append(f"> **Since:** {tags.since}\n")
    if tags.note:
        out.append(f"> **Note:** {tags.note}\n")
    if tags.returns:
        out.append(f"**Returns:** {tags.returns}\n")
    return out


def _render_struct_code(s: StructDef) -> str:
    lines = [f"{s.kind} {s.name}", "{"]
    for f in s.fields:
        lines.append(f"    {f.type_str} {f.name}{f.array_suffix};")
    lines.append("};")
    return "```c\n" + "\n".join(lines) + "\n```"


def _render_field_table(s: StructDef, overlay_fields: dict,
                        struct_map: Optional[Dict[str, "StructDef"]] = None) -> str:
    if not s.fields:
        return ""
    rows = ["| Field | Type | Description |",
            "|-------|------|-------------|"]
    for f in s.fields:
        ov_f = overlay_fields.get(f.name, {})
        desc = ov_f.get('description', '') or f.comment or s.doc.params.get(f.name, "")

        bare = f.type_str.strip()
        if bare.startswith('struct '):
            bare = bare[7:].strip()
        if struct_map and bare in struct_map:
            type_cell = (f"[`{f.type_str}`](#{_struct_anchor(bare)})"
                         f"`{f.array_suffix}`" if f.array_suffix
                         else f"[`{f.type_str}`](#{_struct_anchor(bare)})")
        else:
            type_cell = f"`{f.type_str}{f.array_suffix}`"

        rows.append(f"| `{f.name}` | {type_cell} | {desc} |")
    return "\n".join(rows)


def _render_const_table(defines: List[Define], overlay: dict) -> str:
    rows = ["| Name | Value | Description |",
            "|------|-------|-------------|"]
    for d in defines:
        ov   = _ov(overlay, 'defines', d.name)
        desc = ov.get('description', '') or d.doc.body or ""
        dep  = " ~~(deprecated)~~" if d.doc.deprecated else ""
        rows.append(f"| `{d.name}`{dep} | `{d.value}` | {desc} |")
    return "\n".join(rows)


def _ioctl_direction(macro: str) -> str:
    return {
        '_IO':   'none (no data transfer)',
        '_IOW':  'write (userspace → kernel)',
        '_IOR':  'read  (kernel → userspace)',
        '_IOWR': 'read/write (both directions)',
    }.get(macro, macro)

def _group_defines(defines: List[Define], ioctl_prefix: str) -> Dict[str, List[Define]]:
    """Group #defines by longest shared underscore-delimited token prefix."""
    candidate: Dict[str, List[Define]] = OrderedDict()

    for d in defines:
        if d.name.startswith(ioctl_prefix):
            continue
        parts = d.name.split('_')
        prefix = '_'.join(parts[:-1]) if len(parts) > 1 else d.name
        candidate.setdefault(prefix, []).append(d)

    prefixes = sorted(candidate.keys(), key=len)
    absorbed: Set[str] = set()
    for i, p in enumerate(prefixes):
        if p in absorbed:
            continue
        for q in prefixes:
            if q != p and q not in absorbed and q.startswith(p + '_'):
                candidate[p].extend(candidate[q])
                absorbed.add(q)

    misc: List[Define] = []
    final: Dict[str, List[Define]] = OrderedDict()

    for p in prefixes:
        if p in absorbed:
            continue
        seen: Set[str] = set()
        unique = [d for d in candidate[p] if not (d.name in seen or seen.add(d.name))]
        if len(unique) == 1:
            misc.extend(unique)
        else:
            final[p] = sorted(unique, key=lambda d: d.name)

    if misc:
        final['Miscellaneous'] = sorted(misc, key=lambda d: d.name)

    return final

def render(result: ParseResult, overlay: dict, title: str,
           version: Optional[str], toc: bool, no_meta: bool,
           ioctl_prefix: str) -> str:

    out: List[str] = []

    if version and not no_meta:
        out.append(f'<meta name="pciem-doc-version" content="{version}">\n')

    out.append(f"# {title}\n")
    out.append(
        "This page is **auto-generated** from the PCIem kernel headers. "
        "Do not edit it by hand — run `make docs` to regenerate.\n\n"
        "PCIem exposes a userspace-facing API through `/dev/pciem` that lets "
        "developers configure and emulate PCIe devices entirely from userspace.\n"
    )

    struct_map: Dict[str, StructDef]       = {s.name: s for s in result.structs}
    struct_to_ioctls: Dict[str, List[IoctlDef]] = defaultdict(list)
    for io in result.ioctls:
        if io.struct_name:
            struct_to_ioctls[io.struct_name].append(io)

    define_groups = _group_defines(result.defines, ioctl_prefix)

    if toc:
        out.append("## Contents\n")
        if define_groups:
            out.append("- [Constants](#constants)")
        if result.structs:
            out.append("- [Structures](#structures)")
            for s in result.structs:
                dep = " ~~(deprecated)~~" if s.doc.deprecated else ""
                out.append(f"  - [`{s.name}`](#{_struct_anchor(s.name)}){dep}")
        if result.ioctls:
            out.append("- [IOCTLs](#ioctls)")
            for io in result.ioctls:
                dep = " ~~(deprecated)~~" if io.doc.deprecated else ""
                out.append(f"  - [`{io.name}`](#{_ioctl_anchor(io.name)}){dep}")
        out.append("")

    if define_groups:
        out.append("## Constants\n")
        for prefix, items in define_groups.items():
            heading = "Miscellaneous" if prefix == 'Miscellaneous' else f"`{prefix}_*`"
            out.append(f"### {heading}\n")
            out.append(_render_const_table(items, overlay))
            out.append("")

    if result.structs:
        sources = list(dict.fromkeys(s.source_file for s in result.structs))
        sources_str = ', '.join(f'`{s}`' for s in sources)
        out.append("## Structures\n")
        out.append(f"> *Defined in {sources_str}*\n")
        for s in result.structs:
            ov           = _ov(overlay, 'structs', s.name)
            desc_override = ov.get('description', '')
            dep_badge    = " ⚠️ *Deprecated*" if s.doc.deprecated else ""

            out.append(f"### `{s.name}`{dep_badge} {{#{_struct_anchor(s.name)}}}\n")
            out.extend(_render_doc_tags(s.doc, extra=desc_override))
            out.append(_render_struct_code(s))
            out.append("")

            ft = _render_field_table(s, ov.get('fields', {}), struct_map)
            if ft:
                out.append(ft)
                out.append("")

            refs = struct_to_ioctls.get(s.name)
            if refs:
                links = ', '.join(f"[`{r.name}`](#{_ioctl_anchor(r.name)})" for r in refs)
                out.append(f"**Used by:** {links}\n")

    if result.ioctls:
        out.append("## IOCTLs\n")
        out.append(
            "> All ioctls are issued on the `/dev/pciem` file descriptor "
            "unless noted otherwise.\n"
        )
        for io in result.ioctls:
            ov           = _ov(overlay, 'ioctls', io.name)
            desc_override = ov.get('description', '')
            dep_badge    = " ⚠️ *Deprecated*" if io.doc.deprecated else ""

            out.append(f"### `{io.name}`{dep_badge} {{#{_ioctl_anchor(io.name)}}}\n")

            if io.struct_name:
                macro_str = (f"#define {io.name} "
                             f"{io.macro}({io.magic}, {io.number}, struct {io.struct_name})")
            else:
                macro_str = f"#define {io.name} {io.macro}({io.magic}, {io.number})"

            out.append(f"```c\n{macro_str}\n```\n")
            out.append(f"**Direction:** {_ioctl_direction(io.macro)}\n")
            out.extend(_render_doc_tags(io.doc, extra=desc_override))

            if io.struct_name:
                link = (f"[`{io.struct_name}`](#{_struct_anchor(io.struct_name)})"
                        if io.struct_name in struct_map else f"`{io.struct_name}`")
                out.append(f"**Parameter struct:** {link}\n")
                usage = (
                    f"```c\n"
                    f"struct {io.struct_name} arg = {{ /* ... */ }};\n"
                    f"int ret = ioctl(fd, {io.name}, &arg);\n"
                    f"```\n"
                )
            else:
                usage = (
                    f"```c\n"
                    f"int ret = ioctl(fd, {io.name});\n"
                    f"```\n"
                )
            out.append(usage)

    return "\n".join(out)

_SELFTEST_HEADER = """\
/** @param offset Byte offset within the BAR. */
struct pciem_event {
    uint64_t seq;   /* sequence number */
    uint32_t type;  /* one of PCIEM_EVENT_* */
    uint64_t offset;
};

#define PCIEM_EVENT_MMIO_READ  1  /* driver read from MMIO */
#define PCIEM_EVENT_MMIO_WRITE 2

/// @deprecated Use pciem_event instead.
struct pciem_response {
    uint64_t seq;
    int32_t status;
};

#define PCIEM_IOCTL_MAGIC 0xAF
#define PCIEM_IOCTL_REGISTER _IO(PCIEM_IOCTL_MAGIC, 14)
#define PCIEM_IOCTL_DMA _IOWR(PCIEM_IOCTL_MAGIC, 16, struct pciem_dma_op)
"""


def _run_self_tests() -> int:
    import tempfile, traceback
    failures = 0

    def check(name: str, cond: bool, detail: str = ""):
        nonlocal failures
        status = "PASS" if cond else "FAIL"
        print(f"  {status}  {name}" + (f": {detail}" if not cond and detail else ""))
        if not cond:
            failures += 1

    print("Running self-tests …\n")
    ioctl_re = _make_ioctl_re("PCIEM_IOCTL_")

    with tempfile.NamedTemporaryFile(suffix='.h', mode='w', delete=False) as f:
        f.write(_SELFTEST_HEADER)
        tmp = f.name

    md_tmp = tmp + ".md"
    try:
        r = _parse_file(tmp, ioctl_re, [])

        names = [s.name for s in r.structs]
        check("struct pciem_event parsed",    "pciem_event"    in names)
        check("struct pciem_response parsed", "pciem_response" in names)

        ev = next(s for s in r.structs if s.name == "pciem_event")
        fnames = [f.name for f in ev.fields]
        check("pciem_event.seq",    "seq"    in fnames)
        check("pciem_event.type",   "type"   in fnames)
        check("pciem_event.offset", "offset" in fnames)

        check("@param offset harvested",
              ev.doc.params.get("offset") == "Byte offset within the BAR.")

        type_f = next((f for f in ev.fields if f.name == "type"), None)
        check("inline comment on type field",
              type_f is not None and "PCIEM_EVENT" in type_f.comment)

        resp = next(s for s in r.structs if s.name == "pciem_response")
        check("@deprecated on pciem_response", "pciem_event" in resp.doc.deprecated)

        ioctl_names = [io.name for io in r.ioctls]
        check("PCIEM_IOCTL_REGISTER parsed", "PCIEM_IOCTL_REGISTER" in ioctl_names)
        check("PCIEM_IOCTL_DMA parsed",      "PCIEM_IOCTL_DMA"      in ioctl_names)

        reg = next(io for io in r.ioctls if io.name == "PCIEM_IOCTL_REGISTER")
        check("PCIEM_IOCTL_REGISTER is _IO",           reg.macro == "_IO")
        check("PCIEM_IOCTL_REGISTER has no struct",    reg.struct_name == "")

        dma = next(io for io in r.ioctls if io.name == "PCIEM_IOCTL_DMA")
        check("PCIEM_IOCTL_DMA is _IOWR",              dma.macro == "_IOWR")
        check("PCIEM_IOCTL_DMA struct = pciem_dma_op", dma.struct_name == "pciem_dma_op")

        check("PCIEM_IOCTL_MAGIC not in ioctls",
              "PCIEM_IOCTL_MAGIC" not in ioctl_names)
        check("PCIEM_IOCTL_MAGIC in defines",
              any(d.name == "PCIEM_IOCTL_MAGIC" for d in r.defines))

        groups = _group_defines(r.defines, "PCIEM_IOCTL_")
        check("PCIEM_EVENT constants grouped",
              any("PCIEM_EVENT" in k for k in groups))

        js = json.loads(_to_json(r))
        check("JSON round-trip has structs", "structs" in js)
        check("JSON round-trip has ioctls",  "ioctls"  in js)

        rendered = render(r, {}, "Test", None, False, True, "PCIEM_IOCTL_")
        with open(md_tmp, 'w') as mf:
            mf.write(rendered)
        rc = _check_mode(r, {}, "Test", None, False, True, "PCIEM_IOCTL_", md_tmp)
        check("--check returns 0 for identical output", rc == 0)

        with open(md_tmp, 'w') as mf:
            mf.write("# Different\n")
        rc = _check_mode(r, {}, "Test", None, False, True, "PCIEM_IOCTL_", md_tmp)
        check("--check returns 1 for stale output", rc == 1)

    except Exception:
        traceback.print_exc()
        failures += 1
    finally:
        for p in (tmp, md_tmp):
            try:
                os.unlink(p)
            except OSError:
                pass

    status = "All tests passed." if not failures else f"{failures} test(s) FAILED."
    print(f"\n{status}")
    return failures

def _check_mode(result: ParseResult, overlay: dict, title: str,
                version: Optional[str], toc: bool, no_meta: bool,
                ioctl_prefix: str, output_path: str) -> int:
    """Re-render and diff against output_path. Returns 0=ok, 1=stale, 2=missing."""
    fresh = render(result, overlay, title, version, toc, no_meta, ioctl_prefix)

    if not os.path.exists(output_path):
        print(f"[check] {output_path}: file does not exist", file=sys.stderr)
        return 2

    existing = Path(output_path).read_text()
    if fresh == existing:
        print(f"[check] {output_path}: up to date ✓", file=sys.stderr)
        return 0

    import difflib
    diff = list(difflib.unified_diff(
        existing.splitlines(), fresh.splitlines(),
        fromfile=f"{output_path} (on disk)",
        tofile=f"{output_path} (freshly generated)",
        lineterm='', n=3,
    ))
    print(f"[check] {output_path}: STALE — {len(diff)} diff lines", file=sys.stderr)
    for ln in diff[:80]:
        print(ln, file=sys.stderr)
    if len(diff) > 80:
        print(f"  … {len(diff) - 80} more lines omitted", file=sys.stderr)
    return 1

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate PCIem API docs from C headers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument('headers', nargs='*', help="Input C header file(s)")
    ap.add_argument('-o', '--output', default='-',
                    help="Output file path (default: stdout; required for --check)")
    ap.add_argument('-t', '--title',   default='API Reference')
    ap.add_argument('-v', '--version', default=None)
    ap.add_argument('--desc', default=None, metavar='FILE',
                    help="TOML overlay with hand-written descriptions")
    ap.add_argument('--ioctl-prefix', default='PCIEM_IOCTL_', metavar='PFX',
                    help="Prefix identifying IOCTL #defines (default: PCIEM_IOCTL_)")
    ap.add_argument('--exclude-prefix', action='append', default=[],
                    dest='exclude_prefixes', metavar='PFX',
                    help="Skip items whose names start with PFX (repeatable)")
    ap.add_argument('--toc',       action='store_true', help="Emit a table of contents")
    ap.add_argument('--no-meta',   action='store_true', help="Skip the <meta> version tag")
    ap.add_argument('--json',      action='store_true', help="Output parsed AST as JSON")
    ap.add_argument('--check',     action='store_true',
                    help="Diff rendered output against -o FILE; exit 1 if stale")
    ap.add_argument('--warn-undoc', action='store_true',
                    help="Warn about structs/ioctls with no description")
    ap.add_argument('--self-test', action='store_true',
                    help="Run built-in unit tests and exit")
    args = ap.parse_args()

    if args.self_test:
        return _run_self_tests()

    if not args.headers:
        ap.error("Provide at least one header file, or use --self-test")

    ioctl_re  = _make_ioctl_re(args.ioctl_prefix)
    results   = [_parse_file(h, ioctl_re, args.exclude_prefixes) for h in args.headers]
    combined  = _merge(results)
    overlay   = _load_overlay(args.desc)

    for w in combined.warnings:
        print(f"[warn] {w}", file=sys.stderr)

    if args.warn_undoc:
        for w in _warn_undocumented(combined, overlay):
            print(f"[undoc] {w}", file=sys.stderr)

    if args.json:
        out = _to_json(combined)
        if args.output == '-':
            print(out)
        else:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(out)
            print(f"Written to {args.output}", file=sys.stderr)
        return 0

    if args.check:
        if args.output == '-':
            ap.error("--check requires -o FILE")
        return _check_mode(
            combined, overlay, args.title, args.version,
            args.toc, args.no_meta, args.ioctl_prefix, args.output,
        )

    md = render(combined, overlay, title=args.title, version=args.version,
                toc=args.toc, no_meta=args.no_meta, ioctl_prefix=args.ioctl_prefix)

    if args.output == '-':
        print(md)
    else:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(md)
        print(f"Written to {args.output}", file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
