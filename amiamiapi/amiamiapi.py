import requests
from math import ceil

rootURL = "https://api.amiami.com/api/v1.0/items"
PER_PAGE = 30

class Item:
    def __init__(self, *args, **kwargs):
        self.productURL = kwargs['productURL']
        self.imageURL = kwargs['imageURL']
        self.productName = kwargs['productName']
        self.price = kwargs['price']
        self.productCode = kwargs['productCode']
        self.availability = kwargs['availability']
        self.flags = kwargs['flags']

class ResultSet:

    def __init__(self):
        self.items = []
        self.maxItems = -1
        self.init = False
        self.pages = -1
        self._itemCount = 0

    def add(self, productInfo):
        # Para referencia futura
        # hay 3 flags de stock
        # stock, stock_flg y instock_flg
        # stock es para uso interno de amiami, no para buscar figuras
        # stock_flg es 1 siempre
        # instock_flg es 1 cuando puedes ordenar el item pero
        # instock_flg es 0 cuando existe la página pero no en resultados
        # entonces se usa instock porque nos interesan los resultados
        inStock = productInfo['instock_flg'] == 1
        isClosed = productInfo['order_closed_flg'] == 1
        isPreorder = productInfo['preorderitem'] == 1
        isBackorder = productInfo['list_backorder_available'] == 1
        # Esto se obtuvo a prueba y error con muchas figuras, checando la
        # s_st_condition_flag query que responde la API. No está completamente
        # verificado 
        isPreOwned = productInfo['condition_flg'] == 1
        # Las flags son:
        flags = {
            "instock": inStock,
            "isclosed": isClosed,
            "ispreorder": isPreorder,
            "isbackorder": isBackorder,
            "ispreowned": isPreOwned,
        }
        availability = "Unknown status"
        if isClosed:
            if isPreorder:
                availability = "Pre-order Closed"
            elif isBackorder:
                availability = "Back-order Closed"
            else:
                availability = "Order Closed"
        elif isBackorder:
            availability = "Back-order"
        else:
            if isPreorder and inStock:
                availability = "Pre-order"
            elif isPreOwned and inStock:
                availability = "Pre-owned"
            elif inStock:
                availability = "Available"

        if availability == "Unknown status":
            '''print("STATUS ERROR FOR {}: flags:{}, avail:{}".format(
                productInfo['gcode'],
                flags,
                availability,
            ))'''
        item = Item(
            productURL="https://www.amiami.com/eng/detail/?gcode={}".format(productInfo['gcode']),
            imageURL="https://img.amiami.com{}".format(productInfo['thumb_url']),
            productName=productInfo['gname'],
            price=productInfo['c_price_taxed'],
            productCode=productInfo['gcode'],
            availability=availability,
            flags=flags,
        )
        self.items.append(item)

    def parse(self, obj):
        # true cuando termina
        # false si se puede volver a llamar
        if not self.init:
            self.maxItems = obj['search_result']['total_results']
            self.pages = int(ceil(self.maxItems / float(PER_PAGE)))
            self.init = True
        for productInfo in obj['items']:
            self.add(productInfo)
            self._itemCount += 1

        return self._itemCount == self.maxItems

def search(keywords):
    data = {
        "s_keywords": keywords,
        "pagecnt": 1,
        "pagemax": PER_PAGE,
        "lang": "eng",
    }
    headers = {
        "X-User-Key": "amiami_dev"
    }
    rs = ResultSet()
    while not rs.parse(requests.get(rootURL, data, headers=headers).json()):
        data['pagecnt'] += 1

    return rs