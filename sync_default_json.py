#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ko/default.json을 기준으로 jp, zh default.json을 동기화합니다.
- 알파벳 순서·단어 목록·이미지는 ko와 동일하게 맞춤
- name, value는 기존 jp/zh 파일에서 (letter, word)로 매칭하여 사용
- 매칭되지 않는 단어는 영어 word를 value로 사용
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


def build_word_map(lang_data):
    """(uppercase, word) -> value 매핑 생성"""
    word_map = {}
    for entry in lang_data["data"]:
        letter = entry["uppercase"]
        for w in entry.get("words", []):
            word_map[(letter, w["word"])] = w["value"]
    return word_map


def get_letter_names(lang_data):
    """알파벳별 name(발음) 매핑"""
    return {entry["uppercase"]: entry["name"] for entry in lang_data["data"]}


def sync_from_ko():
    ko_path = DATA_DIR / "ko" / "default.json"
    jp_path = DATA_DIR / "jp" / "default.json"
    zh_path = DATA_DIR / "zh" / "default.json"

    with open(ko_path, "r", encoding="utf-8") as f:
        ko_data = json.load(f)

    with open(jp_path, "r", encoding="utf-8") as f:
        jp_existing = json.load(f)
    with open(zh_path, "r", encoding="utf-8") as f:
        zh_existing = json.load(f)

    jp_word_map = build_word_map(jp_existing)
    zh_word_map = build_word_map(zh_existing)
    jp_names = get_letter_names(jp_existing)
    zh_names = get_letter_names(zh_existing)

    def make_lang_data(word_map, names):
        """ko 구조를 유지하면서 value만 해당 언어로 치환"""
        new_data = {"version": ko_data["version"], "data": []}
        for entry in ko_data["data"]:
            letter = entry["uppercase"]
            new_entry = {
                "uppercase": entry["uppercase"],
                "lowercase": entry["lowercase"],
                "name": names.get(letter, entry["uppercase"]),
                "words": [],
            }
            for w in entry["words"]:
                key = (letter, w["word"])
                value = word_map.get(key, w["word"])  # 없으면 영어 그대로
                new_entry["words"].append({
                    "word": w["word"],
                    "value": value,
                    "image_type": w["image_type"],
                    "image_value": w["image_value"],
                })
            new_data["data"].append(new_entry)
        return new_data

    jp_new = make_lang_data(jp_word_map, jp_names)
    zh_new = make_lang_data(zh_word_map, zh_names)

    with open(jp_path, "w", encoding="utf-8") as f:
        json.dump(jp_new, f, ensure_ascii=False, indent=2)

    with open(zh_path, "w", encoding="utf-8") as f:
        json.dump(zh_new, f, ensure_ascii=False, indent=2)

    print("jp/default.json, zh/default.json 동기화 완료 (ko 기준)")


if __name__ == "__main__":
    sync_from_ko()
