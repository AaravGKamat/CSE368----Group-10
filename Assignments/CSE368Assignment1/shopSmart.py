# shopSmart.py
# ------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 

"""
Here's the intended output of this script, once you fill it in:

Welcome to shop1 fruit shop
Welcome to shop2 fruit shop
For orders:  [('apples', 1.0), ('oranges', 3.0)] best shop is shop1
For orders:  [('apples', 3.0)] best shop is shop2
"""
from __future__ import print_function
import shop


def shopSmart(orderList, fruitShops):
    """
        orderList: List of (fruit, numPound) tuples
        fruitShops: List of FruitShops
    """
    "*** YOUR CODE HERE ***"
    #Check if orderList and fruitShops is viable, return none if not
    if len(orderList) ==0 or len(fruitShops)==0 :
        return None
    
    #Check prices of all stores, set to none for initialized minShop or ignore for other shops if shop
    #does not carry item
    minShop = fruitShops[0]
    minShopTotal = shop.FruitShop.getPriceOfOrder(minShop,orderList)
    if not(checkInventory(orderList,minShop)):
            minShop = None
    for s in fruitShops:
        shopTotal = shop.FruitShop.getPriceOfOrder(s,orderList)
        if shopTotal < minShopTotal and checkInventory(orderList,s):
            minShop = s
    return minShop

def checkInventory(orderList, fruitShop):
    if len(orderList) ==0 or fruitShop==None :
        return False
    for o in orderList:
        if shop.FruitShop.getCostPerPound(fruitShop,o[0]) == None:
            print(o([0]))
            return False
    return True


if __name__ == '__main__':
    "This code runs when you invoke the script from the command line"
    orders = [('apples', 1.0), ('oranges', 3.0)]
    dir1 = {'apples': 2.0, 'oranges': 1.0}
    shop1 = shop.FruitShop('shop1', dir1)
    dir2 = {'apples': 1.0, 'oranges': 5.0}
    shop2 = shop.FruitShop('shop2', dir2)
    shops = [shop1, shop2]
    print("For orders ", orders, ", the best shop is", shopSmart(orders, shops).getName())
    orders = [('apples', 3.0)]
    print("For orders: ", orders, ", the best shop is", shopSmart(orders, shops).getName())
