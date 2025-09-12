from graphviz import Digraph

# Create a flowchart
dot = Digraph(comment="Flowchart for buyLotsOfFruit")

# Nodes
dot.node("A", "Start")
dot.node("B", "Set totalCost = 0.0")
dot.node("C", "For each (fruit, numPounds) in orderList")
dot.node("D", "Is fruit in fruitPrices?", shape="diamond")
dot.node("E", "Print error message\nReturn None", shape="box")
dot.node("F", "totalCost += fruitPrices[fruit] * numPounds")
dot.node("G", "More fruits?", shape="diamond")
dot.node("H", "Return totalCost")
dot.node("I", "End")

# Edges
dot.edges(["AB", "BC"])
dot.edge("C", "D")
dot.edge("D", "E", label="No")
dot.edge("D", "F", label="Yes")
dot.edge("F", "G")
dot.edge("G", "C", label="Yes")
dot.edge("G", "H", label="No")
dot.edge("E", "I")
dot.edge("H", "I")

# Render flowchart to file
file_path = "/mnt/data/buyLotsOfFruit_flowchart"
dot.render(file_path, format="png", cleanup=True)

file_path + ".png"

