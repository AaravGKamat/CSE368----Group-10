# buyLotsOfFruit.py
# -----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.

"""
To run this script, type

  python buyLotsOfFruit.py

Once you have correctly implemented the buyLotsOfFruit function,
the script should produce the output:

Cost of [('apples', 2.0), ('pears', 3.0), ('limes', 4.0)] is 12.25
"""
from __future__ import print_function

fruitPrices = {'apples': 2.00, 'oranges': 1.50, 'pears': 1.75,
               'limes': 0.75, 'strawberries': 1.00}


def buyLotsOfFruit(orderList):
    """
        orderList: List of (fruit, numPounds) tuples

    Returns cost of order
    """
    totalCost = 0.0

    for item in orderList:
        if fruitPrices.keys().__contains__(item[0]):
            totalCost += item[1] * fruitPrices.get(item[0])
        else:
            print(item[0], "does not appear in fruitPrices")
            return None
    
    return totalCost


# Main Method
if __name__ == '__main__':
    "This code runs when you invoke the script from the command line"
    orderList = [('apples', 2.0), ('pears', 3.0), ('limes', 4.0)]
    print('Cost of', orderList, 'is', buyLotsOfFruit(orderList))

    # Additional tests created by Matt
    # orderList = [('apples', 2.5), ('pears', 3.5), ('limes', 4.5)] # expected: $14.50
    # print('Cost of', orderList, 'is', buyLotsOfFruit(orderList))
    # orderList = [('apples', 2.0), ('pears', 3.0), ('limes', 4.0), ("potatoes", 3.5)] # expected: error (potatoes not found)
    # buyLotsOfFruit(orderList)