import sys
sys.path.append(r'D:\borhlang-ime\data')
from convert_dict_v3 import BucRomanizer, LuaDictParser
from pathlib import Path

rom = BucRomanizer()
cpx_data = LuaDictParser.parse_lua_dict(Path(r'D:\borhlang-ime\data\cpx-pron-data.lua'))

# 測試1：gui3 能否生成正確的平話字候選
print('測試 gui3 轉換：')
candidates = rom.psp_to_buc_candidates('gui3')
print('  候選數量:', len(candidates))
for cand in candidates:
    print('  -', repr(cand))

# 測試2：字典中鬼的讀音
print('\\n鬼的字典讀音：')
print(' ', cpx_data.get('鬼', []))

# 測試3：sua1 能否生成 suaⁿ
print('\\n測試 sua1 轉換：')
candidates = rom.psp_to_buc_candidates('sua1')
print('  候選數量:', len(candidates))
for cand in candidates:
    print('  -', repr(cand))

# 測試4：字典中山的讀音
print('\\n山的字典讀音：')
print(' ', cpx_data.get('山', []))