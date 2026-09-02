# -*- coding: utf-8 -*-
"""Java 版进度介绍图渲染（套物品描述同款草方块+泥土配色）"""
import os, json
from PIL import Image, ImageDraw, ImageFont


def _find_font():
    """按平台查找可用中文字体(Windows 优先, 兼容 Linux/macOS)"""
    import os
    cands = [
        r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\msyh.ttf',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/System/Library/Fonts/PingFang.ttc',
    ]
    for p in cands:
        if os.path.exists(p):
            return p
    return cands[0]

FONT = _find_font()
_BASE = os.path.dirname(os.path.abspath(__file__))
ACCOM_MAT = os.path.join(_BASE, 'mcquery_v3', 'Accom_Material')

GRASS = (107, 154, 61)
DIRT = (155, 118, 83)
DIRT_DARK = (120, 88, 60)
BORDER = (78, 52, 46)
TEXT_TITLE = (255, 255, 255)
TEXT_SUB = (230, 240, 210)
TEXT_HEAD = (255, 224, 130)
TEXT_BODY = (248, 236, 210)


def _wrap(draw, text, font, maxw):
    lines = []
    for para in text.splitlines():
        line = ''
        for ch in para:
            if line and draw.textlength(line + ch, font=font) > maxw:
                lines.append(line)
                line = ch
            else:
                line += ch
        if line:
            lines.append(line)
    return lines


def load_icon(name):
    """加载进度物品图标，name 可能是 'Wooden Pickaxe' 或 'Enchanted Book.gif'"""
    if not name:
        return None
    base = name
    for ext in ('.gif', '.png'):
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
            break
    for ext in ('.png', '.gif'):
        p = os.path.join(ACCOM_MAT, base + ext)
        if os.path.exists(p):
            return Image.open(p).convert('RGBA')
    return None


def load_bg(bg):
    p = os.path.join(ACCOM_MAT, f'Advancement-{bg}-raw.png')
    if os.path.exists(p):
        return Image.open(p).convert('RGBA')
    return None


def _compact(text):
    """把 '* a
* b
* c' 列表合并成 'a、b、c' 一行"""
    if not text:
        return text
    result = []
    items = []
    for ln in text.split(chr(10)):
        s = ln.strip()
        if s.startswith('* '):
            items.append(s[2:].strip())
        else:
            if items:
                result.append('、'.join(items))
                items = []
            if s:
                result.append(s)
    if items:
        result.append('、'.join(items))
    return chr(10).join(result)


def build_icon(icon_name, bg):
    """背景框(52x52) + 物品图标(32x32) 叠加，输出 64x64"""
    bg_img = load_bg(bg)
    item = load_icon(icon_name)
    if bg_img is None and item is None:
        return None
    canvas = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    if bg_img is not None:
        bg_img = bg_img.resize((64, 64), Image.LANCZOS)
        canvas.paste(bg_img, (0, 0), bg_img)
    if item is not None:
        # 物品图标按比例 40x40 居中（wiki 中 32px 图标叠在 52px 背景上）
        item = item.resize((40, 40), Image.LANCZOS)
        canvas.paste(item, (12, 12), item)
    return canvas


def render_adv(adv, upstream_name=''):
    """adv: dict 含 title_zh/title_en/desc/require/icon/bg/category"""
    W = 800
    PAD = 36
    f_title = ImageFont.truetype(FONT, 38)
    f_sub = ImageFont.truetype(FONT, 18)
    f_head = ImageFont.truetype(FONT, 24)
    f_body = ImageFont.truetype(FONT, 21)

    sections = [
        ('分类', adv.get('category', '')),
        ('描述', adv.get('desc', '')),
        ('上游进度', upstream_name or '—'),
        ('实际需求', _compact(adv.get('require', '') or '—')),
    ]

    tmp = ImageDraw.Draw(Image.new('RGBA', (W, 1)))
    head_h = 96
    y = head_h + 28
    for head, body in sections:
        y += 30
        y += len(_wrap(tmp, body, f_body, W - PAD * 2)) * 28
        y += 8
    H = y + PAD

    canvas = Image.new('RGBA', (W, H), DIRT)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, W, head_h], fill=GRASS)
    for i in range(8):
        draw.line([0, head_h - 8 + i, W, head_h - 8 + i],
                  fill=(GRASS[0] - i * 3, GRASS[1] - i * 3, GRASS[2] - i * 2))
    draw.rectangle([0, 0, W - 1, H - 1], outline=BORDER, width=6)

    # 图标 + 名字
    icon = build_icon(adv.get('icon', ''), adv.get('bg', 'plain'))
    if icon is not None:
        slot_x, slot_y = PAD, 16
        canvas.paste(icon, (slot_x, slot_y), icon)
        name_x = slot_x + 64 + 26
    else:
        name_x = PAD
        slot_y = 16

    draw.text((name_x, slot_y + 4), adv.get('title_zh', ''), fill=TEXT_TITLE, font=f_title)
    draw.text((name_x, slot_y + 48), adv.get('title_en', ''), fill=TEXT_SUB, font=f_sub)

    line_y = head_h + 20
    draw.line([PAD, line_y, W - PAD, line_y], fill=DIRT_DARK, width=2)

    y = line_y + 22
    for head, body in sections:
        draw.text((PAD, y), head, fill=TEXT_HEAD, font=f_head)
        y += 30
        for ln in _wrap(draw, body, f_body, W - PAD * 2):
            draw.text((PAD, y), ln, fill=TEXT_BODY, font=f_body)
            y += 28
        y += 8

    return canvas.convert('RGB')


if __name__ == '__main__':
    with open(r'mcquery_v3\Accom_Database\advancements.json', encoding='utf-8') as f:
        items = json.load(f)
    key2name = {it['key']: it['title_zh'] for it in items}
    os.makedirs('render_test', exist_ok=True)
    cases = ['石器时代', '获得升级', '末地', '成双成对', '资深怪物猎人']
    for cn in cases:
        adv = next((it for it in items if it['title_zh'] == cn), None)
        if not adv:
            print('✗ 找不到', cn); continue
        up = key2name.get(adv['upstream'], '')
        img = render_adv(adv, up)
        img.save(f'render_test/adv_{cn}.png')
        print(f'✓ {cn} -> render_test/adv_{cn}.png {img.size}')
