def modify_none(dic: dict) -> dict:
    # 回應資料整理: 使用遞迴方式依序判斷 dict 中所有資料
    # 將部分型態定義為 integer 或是 number 的屬性 None 轉為 0, 其餘型態定義為 string 的屬性 None 轉為 ""
    # 使用 List 存放型態定義為 integer 或是 number 的屬性資料
    int_type_list = [
        "base_amount",
        "listing_preference",
        "max_amount",
        "quantity_default",
    ]

    for key, value in dic.items():
        if isinstance(value, list):
            for i, data in enumerate(value):
                if isinstance(data, dict):
                    modify_none(data)
        elif isinstance(value, dict):
            modify_none(value)
        elif (str(key) in int_type_list) and (dic[key] is None):
            dic[key] = 0
        elif dic[key] is None:
            dic[key] = ""
    return dic


def env_convert_for_mail(project: str, env: str) -> str:
    if env == "prod":
        return "Production"
    elif env == "delta":
        return "Delta"
    else:
        return "Beta"
