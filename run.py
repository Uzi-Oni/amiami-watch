import amiamiapi
from amiamiapi import search
from termcolor import colored, cprint

 
figure = input('Nombre de la figura a buscar: ')    
arr_id = []
while True:
    results = search(figure)
    for item in results.items:
        if item.availability == ("Unknown status"):   
            if item.productCode not in arr_id:
                arr_id.append(item.productCode)
                print(colored("{}, {}".format(item.productName, item.productURL) , 'red'))
        if item.availability == ("Pre-order"):   
            if item.productCode not in arr_id:
                arr_id.append(item.productCode)
                print(colored("{}, {}".format(item.productName, item.productURL) , 'green'))
        if item.availability == ("Pre-owned"):   
            if item.productCode not in arr_id:
                arr_id.append(item.productCode)
                print(colored("{}, {}".format(item.productName, item.productURL) , 'yellow'))

    