from unicodedata import normalize as norm

buc_initials = {
    "b": "b",
    "c": "ch", 
    "d": "d",
    "g": "g",
    "h": "h",
    "k": "k",
    "l": "l",
    "m": "m",
    "n": "n",
    "ng": "ng",
    "p": "p",
    "s": "s",
    "t": "t",
    "z": "c",
    "": ""
}

buc_tones = {
    "1": "",
    "2": "́",
    "3": "̂",
    "4": "̍",
    "5": "̄",
    "6": "",
    "7": "̍",
}

buc_finals = {
	"a": [["a", 1], ["aⁿ", 1], ["ah", 1]],
	"ae": [["e", 1]],
	"ah": [["ah", 1]],
	"ai": [["ai", 1]],
	"ang": [["ang", 1]],
	"ao": [["au", 1]],
	"e": [["a̤", 1], ["a̤ⁿ", 1], ["a̤h", 1]],
	"eh": [["eh", 1]],
	"eng": [["eng", 1]],
	"i": [["i", 1], ["ih", 1]],
	"ia": [["ia", 2], ["iaⁿ", 2], ["iah", 2]],
	"iah": [["iah", 2]],
	"ieh": [["iah", 2]],
	"ieng": [["iang", 2]],
	"ieo": [["a̤u", 2], ["a̤uⁿ", 2], ["a̤uh", 2]],
	"ih": [["ih", 1]],
	"ing": [["ing", 1]],
	"iu": [["iu", 2]],
	"ng": [["ng", 1]],
	"o": [["eo", 2], ["eoh", 2]],
	"oe": [["e̤", 1], ["e̤ⁿ", 1]],
	"oeh": [["e̤h", 1]],
	"oeng": [["e̤ng", 1]],
	"oh": [["eoh", 2]],
	"ong": [["eong", 2]],
	"or": [["o̤", 1], ["o̤ⁿ", 1], ["o̤h", 1]],
	"orh": [["o̤h", 1]],
	"orng": [["o̤ng", 1]],
	"ou": [["o", 1]],
	"u": [["u", 1]],
	"ua": [["ua", 2], ["uaⁿ", 2], ["uah", 2]],
	"uah": [["uah", 2]],
	"uang": [["uang", 2]],
	"ue": [["oi", 1], ["oiⁿ", 1], ["oih", 1]],
	"uh": [["uh", 1]],
	"ui": [["ui", 1]],
	"ung": [["ng", 1]],
	"y": [["ṳ", 1]],
	"yh": [["ṳh", 1]],
	"yng": [["ṳng", 1]],
	"yo": [["io̤", 2], ["io̤ⁿ", 2], ["io̤h", 2]],
	"yoh": [["io̤h", 2]],
	"yong": [["io̤ng", 2]]
}

def get_buc_final(f):
    try:
        wrong_final = {
            "au": "ao",
            "iang": "ieng",
            "ieu": "ieo",
            "iau": "ieo",
            "iao": "ieo",
            "uai": "ue",
            "uei": "ue",
            "yoeh": "yeh",
            "yoeng": "yeng",
            "yor": "yo",
            "yorh": "yoh",
            "yorng": "yong"
        }
        if f in wrong_final:
            f = wrong_final[f]
        return buc_finals[f]
    except KeyError:
        return "KEYERROR"

def get_buc_tone(t):
    try:
        return buc_tones[t]
    except KeyError:
        return "KEYERROR"
    
def get_buc_initial(i):
    try:
        return buc_initials[i]
    except KeyError:
        return "KEYERROR"

def psp_syllable_to_buc(s):
    # 驗證輸入格式：必須以數字結尾（聲調）
    if not s or not s[-1].isdigit():
        return ["FORMAT_ERROR"]
    
    # 解析聲母和韻母+聲調
    if s.startswith("ng") and len(s) == 3:
        initial = ""
        finaltone = s
    elif s.startswith("ng") or s.startswith("ch"):
        initial = s[:2]
        finaltone = s[2:]
    elif s[0] in buc_initials:
        initial = s[0]
        finaltone = s[1:]
    else:
        initial = ""
        finaltone = s
    
    # 分離韻母和聲調
    final, tone = finaltone[:-1], finaltone[-1]
    
    # 驗證聲調必須是 1-7
    if tone not in buc_tones:
        return ["TONE_ERROR"]
    
    # 取得平話字聲母、韻母和聲調
    buc_initial = get_buc_initial(initial)
    if buc_initial == "KEYERROR":
        return ["INITIAL_ERROR"]
    
    buc_final_pairs = get_buc_final(final)
    if buc_final_pairs == "KEYERROR":
        return ["FINAL_ERROR"]
    
    buc_tone_symbol = get_buc_tone(tone)
    if buc_tone_symbol == "KEYERROR":
        return ["TONE_ERROR"]
    
    # 組合候選讀音
    candidates = []
    for pair in buc_final_pairs:
        try:
            buc_final, tone_index = pair
            # 處理特殊情況
            if tone == "2" and not final.endswith("h") and buc_final.endswith("h"):
                buc_tone_symbol = buc_tones["7"]
            elif tone != "2" and not final.endswith("h") and buc_final.endswith("h"):
                continue
            elif (initial.startswith("m") or initial.startswith("n") or initial.startswith("ng")) \
                and buc_final.endswith("ⁿ"):
                continue
        except (ValueError, TypeError):
            return ["VALUEERROR"]
        
        # 將聲調符號插入正確位置
        buc_final_tone = buc_final[:tone_index] + buc_tone_symbol + buc_final[tone_index:]
        if tone == "2" and not final.endswith("h") and buc_final.endswith("h"):
            buc_final_tone += "*"
        candidates.append(norm('NFC', buc_initial + buc_final_tone))
    
    return candidates if candidates else ["CONVERSION_ERROR"]

if __name__ == "__main__":    
    while True:
        input_list = input().split()
        print('"' + '", "'.join([' '.join(psp_syllable_to_buc(s)) for s in input_list]) + '"')