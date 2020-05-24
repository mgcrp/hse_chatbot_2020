import json
import pandas as pd
import requests as rq
import uuid
tmp_uuid = 0

def getTopInCategory(n, category_id, max_price, min_price=0, page=1):
    """
    Возвращает `n` первых товаров в категории `category_id` заданым
    ограничением по цене (сортировка по популярности на Яндекс.Маркет)
    
    Параметры:
        n           - int - количество товаров
        category_id - int - ID категории товара
        max_price   - int - максимальная цена товара
        min_price   - int - минимальная цена товара
        page        - int - номер страницы в выдаче (пока что оставил как технический параметр)
    """
    
    _headers = {
        "Host" : "ipa.touch.market.yandex.ru",
        "X-Test-Id" : "",
        "Connection" : "keep-alive",
        "Accept" : "*/*",
        "Accept-Language" : "en-us",
        "Accept-Encoding" : "gzip, deflate, br",
        "Content-Type" : "application/json",
        "Api-Platform" : "IOS",
        "User-Agent" : "WhiteMarket/600.19.1 (ru.yandex.ymarket; build:1172; iOS 13.3.1; iPhone)",
        "X-Platform" : "IOS",
        "Content-Length" : "314",
        "X-App-Version" : "600.19.1",
        "X-Device-Type" : "SMARTPHONE"
    }
    
    _uuid = uuid.uuid4().hex
    
    _payload = json.dumps(
        {
            "params": [
                {
                    "filters": {
                        "allow-collapsing": "1",
                        "glfilter": [],
                        "grhow": "shop",
                        "onstock": "1",
                        "pricefrom": min_price,
                        "priceto": max_price,
                        "show-cutprice": "0"
                    },
                    "hid": category_id,
                    "local-offers-first": 0,
                    "numdoc": n,
                    "page": page,
                    "pp": "SEARCH",
                    "rearr-factors": "search_offline_offers=1",
                    "show-shops": "all",
                    "show-vendors": "all",
                    "text": "",
                    "use-default-offers": "1"
                }
            ]
        }
    )
    
    _response = rq.post(
        "https://ipa.touch.market.yandex.ru/api/v2",
        params={
            "name" : "resolveSearch",
            "rearr_factors" : "market_disable_parametric_search_for_white_except_parametric_specification=0",
            "sections" : "MEDICINE",
            "uuid" : tmp_uuid
        },
        headers=_headers,
        data=_payload
    )
    
    _goods = pd.DataFrame(columns=[
        'id', 'raw_title', 'description',
        'offersCount', 'reviewsCount', 'min_price',
        'max_price', 'avg_price', 'rating', 'ratingCount'
    ])

    for item in _response.json()['collections']['product']:
        _goods = _goods.append(
            pd.Series(
                {
                    'id'           : item['id']            if 'id' in item.keys() else pd.np.nan,
                    'description'  : item['description']   if 'description' in item.keys() else pd.np.nan,
                    'offersCount'  : item['offersCount']   if 'offersCount' in item.keys() else pd.np.nan,
                    'reviewsCount' : item['reviewsCount']  if 'reviewsCount' in item.keys() else pd.np.nan,
                    'min_price'    : item['prices']['min'] if 'prices' in item.keys() else pd.np.nan,
                    'max_price'    : item['prices']['max'] if 'prices' in item.keys() else pd.np.nan,
                    'avg_price'    : item['prices']['avg'] if 'prices' in item.keys() else pd.np.nan,
                    'rating'       : item['rating']        if 'rating' in item.keys() else pd.np.nan,
                    'ratingCount'  : item['ratingCount']   if 'ratingCount' in item.keys() else pd.np.nan,
                    'raw_title'    : item['titles']['raw'] if 'titles' in item.keys() else pd.np.nan
                }
            ), ignore_index=True
        )
    
    return _goods