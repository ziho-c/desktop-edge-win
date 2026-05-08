#!/usr/bin/env python3
"""扫 ZDEW 源码（XAML + C#）提取用户可见英文字符串。"""
import re, json
from pathlib import Path
from collections import Counter

repo = Path(__file__).resolve().parent.parent
strings = Counter()

# XAML 属性中带英文文案的常见属性
XAML_ATTR_RE = re.compile(
    r'(?:Content|Header|Title|ToolTip|Text|Tag|Description|PlaceholderText|Watermark|Label)'
    r'\s*=\s*"([^"{}<>]{2,}?)"'
)
# XAML 文本节点 <Run>X</Run> 或 <TextBlock>X</TextBlock>
XAML_TEXT_NODE_RE = re.compile(r'>([A-Z][^<>{}\n]{1,200}?)<')
# C# 字符串字面量
CS_STR_RE = re.compile(r'"((?:[^"\\]|\\.){2,}?)"')

NOT_UI = {
    'true', 'false', 'null', 'undefined', 'utf-8', 'utf8', 'POST', 'GET',
    'PUT', 'DELETE', 'PATCH', 'application/json', 'no-cache',
    'click', 'change', 'submit', 'load', 'error', 'success',
    'small', 'medium', 'large', 'block', 'inline', 'none',
    'left', 'right', 'top', 'bottom', 'center', 'auto',
    'normal', 'bold', 'italic', 'White', 'Black', 'Red', 'Green', 'Blue',
    'Stretch', 'Center', 'Left', 'Right', 'Top', 'Bottom', 'Pack', 'Default',
    'Visible', 'Hidden', 'Collapsed', 'Auto',
}

SKIP = [
    re.compile(r'^[\s\W\d]+$'),
    re.compile(r'^[a-z][a-zA-Z0-9_-]*$'),  # camelCase 标识符
    re.compile(r'[/\\]'),
    re.compile(r'^https?://'),
    re.compile(r'^[A-Z_][A-Z0-9_]+$'),  # 大写常量
    re.compile(r'^\.[\w-]+'),
    re.compile(r'^#[\w-]+'),
    re.compile(r'^\$\{'),
    re.compile(r'^\{[Bb]inding'),
    re.compile(r'^\{StaticResource'),
    re.compile(r'^\{x:'),
    re.compile(r'pack://'),
    re.compile(r'^[A-Z][a-zA-Z]+\.'),  # Class.Member
    re.compile(r'^\{0\}'),
    re.compile(r'^\d+,\d+'),  # margin 之类
    re.compile(r'^[\d.]+\s*$'),
    re.compile(r'<[a-zA-Z]'),
    re.compile(r'^\s*\\'),
    re.compile(r'^px$|^em$|^%$'),
]


def is_ui(s: str) -> bool:
    s = s.strip()
    if len(s) < 2 or len(s) > 200:
        return False
    if s in NOT_UI:
        return False
    if not re.search(r'[A-Za-z]', s):
        return False
    if not s[0].isalpha():
        return False
    if re.search(r'[一-鿿]', s):
        return False
    for p in SKIP:
        if p.search(s):
            return False
    has_space = ' ' in s
    starts_upper = s[0].isupper()
    if not (starts_upper or has_space):
        return False
    if not has_space and re.match(r'^[a-zA-Z][a-zA-Z0-9]+[A-Z]', s):
        return False
    if re.search(r'[{};=\[\]]', s):
        return False
    # XAML 属性值常含 PascalCase 类型名（HorizontalAlignment）但不会有空格 + 长 - 跳过
    if not has_space and len(s) > 25:
        return False
    return True


def extract_xaml(text: str):
    out = []
    for m in XAML_ATTR_RE.findall(text):
        s = m.strip()
        if is_ui(s):
            out.append(s)
    for m in XAML_TEXT_NODE_RE.findall(text):
        s = m.strip()
        if is_ui(s):
            out.append(s)
    return out


def extract_cs(text: str):
    out = []
    for m in CS_STR_RE.finditer(text):
        s = m.group(1).strip()
        if is_ui(s):
            out.append(s)
    return out


def main():
    targets = []
    for p in (repo / 'DesktopEdge').rglob('*'):
        if p.suffix in ('.xaml', '.cs') and 'obj' not in str(p) and 'bin' not in str(p):
            targets.append(p)

    for p in targets:
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        if p.suffix == '.xaml':
            for s in extract_xaml(text):
                strings[s] += 1
        elif p.suffix == '.cs':
            for s in extract_cs(text):
                strings[s] += 1

    out_path = repo / 'scripts' / 'extracted-strings.json'
    sorted_items = sorted(strings.items(), key=lambda x: (-x[1], x[0]))
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump([{"en": s, "freq": n} for s, n in sorted_items], f, ensure_ascii=False, indent=2)
    print(f"Total unique: {len(strings)}; saved to {out_path}")
    print("Top 30:")
    for s, n in sorted_items[:30]:
        print(f"  [{n:3d}] {s}")


if __name__ == '__main__':
    main()
