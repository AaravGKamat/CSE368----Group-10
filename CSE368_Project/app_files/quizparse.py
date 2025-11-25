import os
from pymongo import MongoClient

# testdata = "<Question: What is the largest planet in our solar system? ,^^Choices: &&Choice1:Earth &&Choice1:Mars &&Choice1:Jupiter &&Choice1:Saturn &&Choice1:Venus, **Answer:Jupiter>||<Question: Which planet is known as the Red Planet? ,^^Choices: &&Choice1:Jupiter &&Choice1:Mars &&Choice1:Mercury &&Choice1:Venus &&Choice1:Saturn, **Answer:Mars>||<Question: What is the main component of the Sun? ,^^Choices: &&Choice1:Helium &&Choice1:Hydrogen &&Choice1:Oxygen &&Choice1:Carbon &&Choice1:Nitrogen, **Answer:Hydrogen>||<Question: How long does it take Earth to complete one orbit around the Sun? ,^^Choices: &&Choice1:365 days &&Choice1:24 hours &&Choice1:30 days &&Choice1:12 months &&Choice1:1 week, **Answer:365 days>||<Question: Which planet has the most moons? ,^^Choices: &&Choice1:Earth &&Choice1:Jupiter &&Choice1:Mars &&Choice1:Saturn &&Choice1:Neptune, **Answer:Jupiter>||<Question: What is the primary reason for seasons on Earth? ,^^Choices: &&Choice1:Distance from the Sun &&Choice1:Earth's axial tilt &&Choice1:Moon's gravitational pull &&Choice1:Earth's rotation &&Choice1:Solar flares, **Answer:Earth's axial tilt>||<Question: Which celestial object is considered a dwarf planet? ,^^Choices: &&Choice1:Pluto &&Choice1:Jupiter &&Choice1:Mars &&Choice1:Venus &&Choice1:Mercury, **Answer:Pluto>||<Question: Which planet is closest to the Sun? ,^^Choices: &&Choice1:Mercury &&Choice1:Venus &&Choice1:Earth &&Choice1:Mars &&Choice1:Jupiter, **Answer:Mercury>||<Question: Why does Mercury experience extreme temperature variations? ,^^Choices: &&Choice1:It has no atmosphere &&Choice1:It is very far from the Sun &&Choice1:It rotates too slowly &&Choice1:It has many volcanoes &&Choice1:It is constantly raining, **Answer:It has no atmosphere>||<Question: How does the distance of a planet from the Sun generally affect its orbital period? ,^^Choices: &&Choice1:Closer planets have longer orbits &&Choice1:Distance does not matter &&Choice1:Closer planets have shorter orbits &&Choice1:Farthest planets rotate faster &&Choice1:All planets have the same orbital period, **Answer:Closer planets have shorter orbits>"

# Parses a quiz question input string into a dictionary.


def parse_question(input_str):
    raw_quiz = input_str.split("<>Question:")
    pairs =[]
    count =0
    for pair in raw_quiz:
        if pair!="":
            json_pair = {}
            temp = pair.replace("\n","")
            temp = temp.split("**Answer:")
            print(temp)
            if len(temp) ==2:
                json_pair["question"] = temp[0]
                json_pair["answer"] = temp[1]
                json_pair["count"] = count
                if count ==0:
                    json_pair["start"] = "show"
                count+=1
                pairs.append(json_pair)
    print(pairs)
    return render_template("flash.html",flash_list=pairs,flash_length=len(pairs))