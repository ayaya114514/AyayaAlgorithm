"""Add conservative editorial topic hints to the official PAT directory."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Site-maintained hints, not official PAT tags. Unreviewed titles stay unclassified.
GROUPS = {
    "链表": {"B": [1025, 1075], "A": [1032, 1052, 1074, 1097, 1112, 1133, 1161, 1165]},
    "栈": {"A": [1051, 1086]},
    "队列": {"A": [1014, 1017, 1026]},
    "堆": {"A": [1057, 1129, 1147, 1155, 1171]},
    "树": {"A": [1004, 1020, 1043, 1053, 1064, 1066, 1079, 1086, 1090, 1094, 1099, 1102, 1106, 1110, 1115, 1119, 1123, 1127, 1130, 1135, 1143, 1151, 1159, 1162, 1167, 1174]},
    "图": {"A": [1003, 1013, 1018, 1021, 1030, 1034, 1072, 1076, 1087, 1111, 1122, 1126, 1131, 1134, 1139, 1142, 1146, 1148, 1150, 1154, 1163, 1166, 1170, 1172, 1175]},
    "并查集": {"A": [1107, 1114, 1118]},
    "动态规划": {"A": [1007, 1040, 1045, 1048, 1068]},
    "搜索与回溯": {"A": [1103, 1138, 1160]},
    "贪心": {"B": [1020, 1023, 1070], "A": [1033, 1037, 1038, 1070, 1113, 1125]},
    "数组与双指针": {"B": [1008, 1085], "A": [1029, 1044, 1085]},
    "区间数据结构": {"A": [1046, 1173]},
    "排序与查找": {"B": [1004, 1015, 1028, 1055, 1060, 1080, 1095], "A": [1010, 1012, 1016, 1025, 1028, 1036, 1055, 1062, 1067, 1075, 1080, 1083, 1089, 1095, 1098, 1101, 1109, 1137, 1141, 1169]},
    "哈希与集合": {"B": [1021, 1033, 1039, 1042, 1064, 1065, 1083, 1090, 1093], "A": [1022, 1039, 1041, 1047, 1050, 1054, 1063, 1071, 1078, 1084, 1092, 1120, 1121, 1144, 1145, 1149, 1153, 1157]},
    "字符串": {"B": [1002, 1003, 1009, 1014, 1017, 1024, 1031, 1043, 1047, 1048, 1052, 1067, 1078, 1081, 1084], "A": [1001, 1005, 1023, 1031, 1035, 1060, 1061, 1073, 1077, 1082, 1108, 1140]},
    "数学与数论": {"B": [1007, 1013, 1016, 1022, 1034, 1046, 1051, 1056, 1057, 1062, 1074, 1079, 1086, 1087, 1091, 1094, 1099], "A": [1002, 1009, 1015, 1019, 1024, 1049, 1058, 1059, 1065, 1069, 1081, 1088, 1096, 1100, 1104, 1116, 1132, 1136, 1152, 1156, 1168]},
}


def main():
    path = ROOT / "public" / "data" / "pat.json"
    catalog = json.loads(path.read_text())
    lookup = {}
    for category, levels in GROUPS.items():
        for level, labels in levels.items():
            for label in labels:
                lookup[f"PAT-{level}{label}"] = category
    tagged = 0
    for problem in catalog["problems"]:
        category = lookup.get(problem["id"])
        problem["category"] = category or "待分类"
        problem["tags"] = [category] if category else []
        tagged += bool(category)
    catalog["classification_note"] = "分类为本站整理的学习提示，非官方标签；未核对的条目保留待分类。"
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PAT directory: {len(catalog['problems'])} entries; {tagged} topic hints.")


if __name__ == "__main__":
    main()
