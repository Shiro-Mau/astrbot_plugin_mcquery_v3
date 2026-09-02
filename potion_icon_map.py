# -*- coding: utf-8 -*-
"""药水/酿造相关图标名映射：brewing 里的名字 → Material 图标名"""

# 直接复用映射（无独立图标的药水/材料）
POTION_ICON_FIX = {
    'Redstone Dust': 'Redstone',
    'Mundane Potion': 'Awkward Potion',
    'Mundane Splash Potion': 'Awkward Splash Potion',
    'Mundane Lingering Potion': 'Awkward Lingering Potion',
    'Splash Mundane Potion': 'Awkward Splash Potion',
    'Lingering Mundane Potion': 'Awkward Lingering Potion',
    'Thick Potion': 'Awkward Potion',
    'Thick Splash Potion': 'Awkward Splash Potion',
    'Thick Lingering Potion': 'Awkward Lingering Potion',
    'Splash Thick Potion': 'Awkward Splash Potion',
    'Lingering Thick Potion': 'Awkward Lingering Potion',
    'Long Mundane Potion': 'Awkward Potion',
    'Splash Long Mundane Potion': 'Awkward Splash Potion',
    'Lingering Long Mundane Potion': 'Awkward Lingering Potion',
    # 1.21.6 新矿物（wiki 尚未上传 Invicon），暂用占位
    'Silver': None,
    # 药箭的代表图标是喷溅药箭
    'Tipped Arrow': 'Arrow of Splashing',
}


def potion_icon(name):
    """药水名 → 图标名。Extended/Enhanced 复用基础图标。"""
    base = name.replace(' Extended', '').replace(' Enhanced', '').strip()
    return POTION_ICON_FIX.get(base, base)
