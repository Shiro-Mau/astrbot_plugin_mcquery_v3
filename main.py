# -*- coding: utf-8 -*-
"""MauSeek 我的世界查询插件 v3：.mq 物品 / .cj 成就，图片输出。"""
import asyncio, re

import astrbot.core.message.components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

from .query_engine import query_item, query_achievement, catalog_all


def _clean(text):
    return re.sub(r"\[MSG_ID:\d+\]", "", (text or "")).strip()


def _chain(paths, tip=''):
    chain = [Comp.Image.fromFileSystem(p) for p in paths]
    if tip:
        chain.append(Comp.Plain(tip))
    return chain


@register("astrbot_plugin_mcquery_v3", "Shiro_Mau", "一个普通的mc工具箱", "3.0.0")
class MCQueryV3(Star):
    def __init__(self, context: Context, config=None):
        super().__init__(context)
        self.config = config or {}

    @filter.regex(r"^\.mq(?:\s+|$)")
    async def mq_cmd(self, event: AstrMessageEvent):
        text = _clean(event.message_str)
        parts = text.split()
        rest = parts[1:] if len(parts) > 1 else []
        if not rest:
            yield event.plain_result("用法：.mq 物品名（查描述+配方），.mq 物品 / .mq 方块（看目录）")
            return
        head = rest[0]
        if head in ('物品', '方块'):
            kind = 'item' if head == '物品' else 'block'
            yield event.plain_result('目录有点多，渲染中，稍等哦～')
            paths = await asyncio.to_thread(catalog_all, kind)
            yield event.chain_result([Comp.Image.fromFileSystem(p) for p in paths])
            return
        name = ' '.join(rest)
        imgs, tip = await asyncio.to_thread(query_item, name)
        if not imgs:
            yield event.plain_result(tip)
            return
        yield event.chain_result(_chain(imgs, tip))

    @filter.regex(r"^\.cj(?:\s+|$)")
    async def cj_cmd(self, event: AstrMessageEvent):
        text = _clean(event.message_str)
        parts = text.split()
        rest = parts[1:] if len(parts) > 1 else []
        if not rest:
            yield event.plain_result("用法：.cj 成就名（查成就），.cj 成就（看成就目录）")
            return
        if rest[0] == '成就':
            yield event.plain_result('成就目录来啦，稍等～')
            paths = await asyncio.to_thread(catalog_all, 'adv')
            yield event.chain_result([Comp.Image.fromFileSystem(p) for p in paths])
            return
        name = ' '.join(rest)
        imgs, tip = await asyncio.to_thread(query_achievement, name)
        if not imgs:
            yield event.plain_result(tip)
            return
        yield event.chain_result(_chain(imgs, tip))
