#!/usr/bin/env python3
"""粗暴中文化 ZDEW 源码（XAML + C#）。"""
import re, json
from pathlib import Path


def load_translations(repo_root: Path) -> dict:
    with open(repo_root / 'scripts' / 'translations.json', encoding='utf-8') as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith('_')}


def replace_in_xaml_attr(content: str, en: str, zh: str) -> str:
    """替换 XAML 里 Content/Header/Title/ToolTip/Text/Tag/Description/PlaceholderText/Watermark/Label 属性的英文值。"""
    attrs = '(?:Content|Header|Title|ToolTip|Text|Tag|Description|PlaceholderText|Watermark|Label)'
    # 单独成属性 Foo="X"
    pattern = r'(' + attrs + r'\s*=\s*")' + re.escape(en) + r'(")'
    return re.sub(pattern, r'\g<1>' + zh + r'\g<2>', content)


def replace_in_xaml_text_node(content: str, en: str, zh: str) -> str:
    """替换 XAML 文本节点 >X<。"""
    return re.sub(r'>(\s*)' + re.escape(en) + r'(\s*)<',
                  r'>\1' + zh + r'\2<', content)


def replace_in_cs_string(content: str, en: str, zh: str) -> str:
    """替换 C# 字符串字面量 "X"。注意只动双引号，避免破坏代码。"""
    return content.replace(f'"{en}"', f'"{zh}"')


def translate_file(path: Path, translations: dict) -> int:
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return 0
    original = text

    items = sorted(translations.items(), key=lambda kv: -len(kv[0]))

    for en, zh in items:
        if path.suffix == '.xaml':
            text = replace_in_xaml_attr(text, en, zh)
            text = replace_in_xaml_text_node(text, en, zh)
        elif path.suffix == '.cs':
            text = replace_in_cs_string(text, en, zh)

    if text != original:
        path.write_text(text, encoding='utf-8')
        return 1
    return 0


def main():
    repo = Path(__file__).resolve().parent.parent
    translations = load_translations(repo)
    print(f"Loaded {len(translations)} translations")

    targets = []
    for p in (repo / 'DesktopEdge').rglob('*'):
        if p.suffix not in ('.xaml', '.cs'):
            continue
        if 'obj' in str(p) or 'bin' in str(p):
            continue
        targets.append(p)

    changed = 0
    for p in targets:
        changed += translate_file(p, translations)
    print(f"Scanned {len(targets)} files, modified {changed}")


if __name__ == '__main__':
    main()
