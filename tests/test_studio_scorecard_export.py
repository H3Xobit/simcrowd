"""Scorecard export stays locked while the API health check is pending."""

from __future__ import annotations

import re
from pathlib import Path

PAGE_PATH = Path(__file__).resolve().parents[1] / "web" / "app" / "app" / "page.tsx"


def _page() -> str:
    return PAGE_PATH.read_text(encoding="utf-8")


def _balanced(src: str, open_at: int, open_ch: str, close_ch: str) -> str:
    depth = 0
    quote = ""
    i = open_at
    while i < len(src):
        ch = src[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch in ("'", '"', "`"):
            quote = ch
            i += 1
            continue
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return src[open_at : i + 1]
        i += 1
    raise AssertionError(f"unbalanced {open_ch}{close_ch}")


def _function_body(src: str, name: str) -> str:
    marker = f"function {name}("
    start = src.index(marker)
    brace = src.index("{", start)
    return _balanced(src, brace, "{", "}")[1:-1]


def _download_button(src: str) -> str:
    needle = "onClick={downloadScorecardCsv}"
    at = src.index(needle)
    start = src.rfind("<button", 0, at)
    end = src.index("</button>", at)
    return src[start:end]


def _disabled_expr(button: str) -> str:
    match = re.search(r"disabled=\{([^}]+)\}", button)
    assert match is not None
    return match.group(1).strip()


def _eval_flag(expr: str, mode: str, busy: bool) -> bool:
    if expr.strip() == "res.ok":
        return True
    text = re.sub(
        r"""mode\s*===\s*(["'])([^"']+)\1""",
        lambda match: f"(mode == {match.group(2)!r})",
        expr.strip(),
    )
    text = text.replace("||", " or ").replace("&&", " and ")
    scan = re.sub(r"'[^']*'|\"[^\"]*\"", "", text)
    idents = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", scan))
    if not idents <= {"mode", "busy", "or", "and"}:
        raise AssertionError(f"unsupported expression: {expr}")
    return bool(eval(text, {"__builtins__": {}}, {"mode": mode, "busy": busy}))


def _skip_ws(src: str, i: int) -> int:
    while i < len(src) and src[i].isspace():
        i += 1
    return i


def _skip_quoted(src: str, i: int) -> int:
    quote = src[i]
    i += 1
    while i < len(src):
        if src[i] == "\\":
            i += 2
            continue
        if src[i] == quote:
            return i + 1
        i += 1
    raise AssertionError("unclosed string")


def _read_statement(src: str, i: int) -> tuple[str, int]:
    i = _skip_ws(src, i)
    start = i
    match = re.match(r"(try|if|for|while)\b", src[i:])
    if match:
        i += match.end()
        i = _skip_ws(src, i)
        if i < len(src) and src[i] == "(":
            i += len(_balanced(src, i, "(", ")"))
            i = _skip_ws(src, i)
        if i < len(src) and src[i] == "{":
            i += len(_balanced(src, i, "{", "}"))
            if match.group(1) == "try":
                j = _skip_ws(src, i)
                if src.startswith("catch", j):
                    i = j + len("catch")
                    i = _skip_ws(src, i)
                    if i < len(src) and src[i] == "(":
                        i += len(_balanced(src, i, "(", ")"))
                        i = _skip_ws(src, i)
                    if i < len(src) and src[i] == "{":
                        i += len(_balanced(src, i, "{", "}"))
            return src[start:i].strip(), i
    while i < len(src):
        ch = src[i]
        if ch in ("'", '"', "`"):
            i = _skip_quoted(src, i)
            continue
        if ch == "{":
            i += len(_balanced(src, i, "{", "}"))
            continue
        if ch == "(":
            i += len(_balanced(src, i, "(", ")"))
            continue
        if ch == ";":
            return src[start : i + 1].strip(), i + 1
        i += 1
    tail = src[start:].strip()
    return tail, len(src)


def _statements(body: str) -> list[str]:
    stmts: list[str] = []
    i = 0
    while i < len(body):
        i = _skip_ws(body, i)
        if i >= len(body):
            break
        stmt, i = _read_statement(body, i)
        if stmt:
            stmts.append(stmt)
    return stmts


def _block_body(stmt: str) -> str:
    brace = stmt.index("{")
    return _balanced(stmt, brace, "{", "}")[1:-1]


def _if_condition(stmt: str) -> str:
    paren = stmt.index("(")
    return _balanced(stmt, paren, "(", ")")[1:-1].strip()


def simulate_download(body: str, mode: str, busy: bool, scorecard_present: bool) -> dict:
    """Run the extracted download function until a return or a CSV click."""
    fetches: list[str] = []
    downloads: list[str] = []
    stopped = "end"

    def walk(stmts: list[str]) -> bool:
        nonlocal stopped
        for stmt in stmts:
            early = re.fullmatch(r"if\s*\(.*\)\s*return\s*;", stmt, re.S)
            if early and _eval_flag(_if_condition(stmt), mode, busy):
                stopped = "guard"
                return True
            if stmt.startswith("try"):
                if walk(_statements(_block_body(stmt))):
                    return True
                continue
            if stmt.startswith("if"):
                if _eval_flag(_if_condition(stmt), mode, busy):
                    if walk(_statements(_block_body(stmt))):
                        return True
                continue
            if "fetch(" in stmt and "/scorecard.csv" in stmt:
                fetches.append("/scorecard.csv")
                continue
            if re.fullmatch(r"return\s*;", stmt):
                stopped = "return"
                return True
            if "a.click()" in stmt or ".click()" in stmt:
                kind = "live" if fetches else "showcase"
                if kind == "showcase" and scorecard_present:
                    kind = "scorecard"
                downloads.append(kind)
                stopped = "download"
        return False

    walk(_statements(body))
    return {"fetches": fetches, "downloads": downloads, "stopped": stopped}


def user_click(src: str, mode: str, busy: bool, scorecard_present: bool) -> dict:
    """A disabled button does not dispatch the click. An enabled one calls the handler."""
    button = _download_button(src)
    disabled = _eval_flag(_disabled_expr(button), mode, busy)
    if disabled:
        return {"dispatched": False, "fetches": [], "downloads": [], "stopped": "disabled"}
    result = simulate_download(
        _function_body(src, "downloadScorecardCsv"),
        mode,
        busy,
        scorecard_present,
    )
    result["dispatched"] = True
    return result


def test_checking_mode_click_does_not_export() -> None:
    src = _page()
    assert '{mode === "checking" && "Checking API..."}' in src
    click = user_click(src, mode="checking", busy=False, scorecard_present=False)
    assert click["dispatched"] is False
    assert click["fetches"] == []
    assert click["downloads"] == []
    direct = simulate_download(
        _function_body(src, "downloadScorecardCsv"),
        mode="checking",
        busy=False,
        scorecard_present=False,
    )
    assert direct["stopped"] == "guard"
    assert direct["fetches"] == []
    assert direct["downloads"] == []


def test_download_enabled_again_for_live_and_demo() -> None:
    src = _page()
    body = _function_body(src, "downloadScorecardCsv")
    for mode in ("live", "demo"):
        click = user_click(src, mode=mode, busy=False, scorecard_present=False)
        assert click["dispatched"] is True
    live = simulate_download(body, mode="live", busy=False, scorecard_present=False)
    assert live["fetches"] == ["/scorecard.csv"]
    assert live["downloads"] == ["live"]
    demo = simulate_download(body, mode="demo", busy=False, scorecard_present=False)
    assert demo["fetches"] == []
    assert demo["downloads"] == ["showcase"]


def test_busy_still_blocks_direct_export() -> None:
    src = _page()
    direct = simulate_download(
        _function_body(src, "downloadScorecardCsv"),
        mode="live",
        busy=True,
        scorecard_present=False,
    )
    assert direct["stopped"] == "guard"
    assert direct["fetches"] == []
    assert direct["downloads"] == []
