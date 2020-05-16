import uuid
import numpy as np
import requests as rq


def getDataByYandexID(yandex_id):
    output = {}

    # Part 1 - get basic information, such as name and description

    _uuid = uuid.uuid4().hex
    _baseUrl = f'https://mobile.market.yandex.net/market/white/v2.1.5/models/{yandex_id}'
    _params = {
        'count': '10',
        'fields': 'SHOP_RATING,OFFER_OFFERS_LINK,OFFER_SHOP,OFFER_DELIVERY,OFFER_DISCOUNT,FILTERS,FILTER_FOUND,'
                  'FILTER_PHOTO_PICKER,FILTER_SORTS,OFFER_ACTIVE_FILTERS,PHOTO',
        'groupBy': 'SHOP',
        'local_offers_first': '0',
        'onstock': '1',
        'page': '1',
        'pp': '531',
        'sort': 'RELEVANCY',
        'rearr_factors': 'market_disable_parametric_search_for_white_except_parametric_specification=0',
        'sections': 'MEDICINE',
        'uuid': _uuid
    }
    _headers = {
        'Host': 'mobile.market.yandex.net',
        'Accept': '*/*',
        'Accept-Language': 'en-us',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Test-Id': '',
        'Api-Platform': 'IOS',
        'User-Agent': 'WhiteMarket/600.19.1 (ru.yandex.ymarket; build:1172; iOS 13.3.1; iPhone)',
        'X-Platform': 'IOS',
        'X-App-Version': '600.19.1',
        'Connection': 'keep-alive',
        'X-Device-Type': 'SMARTPHONE'
    }

    _request = rq.get(
        url=_baseUrl,
        headers=_headers,
        params=_params
    )

    output['name'] = _request.json()['model']['name']
    output['description'] = _request.json()['model']['description']
    output['market_link'] = _request.json()['model']['link']
    output['photo'] = _request.json()['model']['photo']['url']

    # Part 2 - get offers

    _params = {
        'count': '10',
        'fields': 'SHOP_RATING,OFFER_OFFERS_LINK,OFFER_SHOP,OFFER_DELIVERY,OFFER_DISCOUNT,FILTERS,FILTER_FOUND,'
                  'FILTER_PHOTO_PICKER,FILTER_SORTS,OFFER_ACTIVE_FILTERS',
        'groupBy': 'SHOP',
        'local_offers_first': '0',
        'onstock': '1',
        'page': '1',
        'pp': '531',
        'sort': 'RELEVANCY',
        'rearr_factors': 'market_disable_parametric_search_for_white_except_parametric_specification=0',
        'sections': 'MEDICINE',
        'uuid': _uuid
    }

    _offers = []
    _baseUrl = f'https://mobile.market.yandex.net/market/white/v2.1.5/models/{yandex_id}/offers'

    _response = rq.get(
        url=_baseUrl,
        headers=_headers,
        params=_params
    )

    _offers.extend(_response.json()['offers'])
    _curPage = 2
    _maxPage = _response.json()['context']['page']['total']

    while _curPage < _maxPage:
        _params['page'] = _curPage
        _response = rq.get(
            url=_baseUrl,
            headers=_headers,
            params=_params
        )
        _offers.extend(_response.json()['offers'])
        _curPage += 1

    _prices = [float(offer['price']['value']) for offer in _offers]

    output['max_price'] = max(_prices)
    output['min_price'] = min(_prices)
    output['count_offers'] = len(_offers)
    output['best_offer'] = _offers[np.argmin(_prices)]

    # Part 3 - get specifications

    _baseUrl = f'https://mobile.market.yandex.net/market/white/v2.1.5/models/{yandex_id}/specification'
    _params = {
        'rearr_factors': 'market_disable_parametric_search_for_white_except_parametric_specification=0',
        'sections': 'MEDICINE',
        'uuid': _uuid
    }

    _response = rq.get(
        url=_baseUrl,
        headers=_headers,
        params=_params
    )
    output['specification'] = _response.json()['specification'][0]

    return output
