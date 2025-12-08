#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試聖經對齊邏輯"""

import re

buc_line = "5:19 Ngâ-le̍h saⁿ Î-do̤̍h āu, cāi sa̤̍ bā̤-bā níng, ho̤h ca̍i saⁿ náng-dṳ̂-giô̤ⁿ:"
hanzi_line = "雅列生以諾後，在世八百年，復再生男女囝。"

# 移除小節標記
buc_text = re.sub(r'^\d+:\d+\s+', '', buc_line)
hanzi_text = hanzi_line

print("平話字文本:", buc_text)
print("漢字文本:", hanzi_text)
print()

# 移除標點符號，但保留空格
buc_no_punct = re.sub(r'[,，;；:.。:：!！?？、]', '', buc_text)
hanzi_no_punct = re.sub(r'[,，;；:.。:：!！?？、]', '', hanzi_text)

print("去標點後:")
print("平話字:", buc_no_punct)
print("漢字:", hanzi_no_punct)
print()

# 分割為詞
buc_words = buc_no_punct.split()
hanzi_words = hanzi_no_punct.split()

print(f"平話字詞數: {len(buc_words)}")
print("平話字詞:", buc_words)
print()
print(f"漢字詞數: {len(hanzi_words)}")
print("漢字詞:", hanzi_words)
print()

# 問題：漢字沒有空格分隔！
# 需要另一種方法
