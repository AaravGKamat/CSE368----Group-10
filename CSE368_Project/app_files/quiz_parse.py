import os
from pymongo import MongoClient
import re
from app_files.database import db

# run the following in mongosh for testing
"""
db.quizzes.insertOne({
  quiz_name: "test_quiz",
  quiz_questions: "<Question: What is the largest planet in our solar system? ,^^Choices: &&Choice1:Earth &&Choice1:Mars &&Choice1:Jupiter &&Choice1:Saturn &&Choice1:Venus, **Answer:Jupiter>||<Question: Which planet is known as the Red Planet? ,^^Choices: &&Choice1:Jupiter &&Choice1:Mars &&Choice1:Mercury &&Choice1:Venus &&Choice1:Saturn, **Answer:Mars>||<Question: What is the main component of the Sun? ,^^Choices: &&Choice1:Helium &&Choice1:Hydrogen &&Choice1:Oxygen &&Choice1:Carbon &&Choice1:Nitrogen, **Answer:Hydrogen>||<Question: How long does it take Earth to complete one orbit around the Sun? ,^^Choices: &&Choice1:365 days &&Choice1:24 hours &&Choice1:30 days &&Choice1:12 months &&Choice1:1 week, **Answer:365 days>||<Question: Which planet has the most moons? ,^^Choices: &&Choice1:Earth &&Choice1:Jupiter &&Choice1:Mars &&Choice1:Saturn &&Choice1:Neptune, **Answer:Jupiter>||<Question: What is the primary reason for seasons on Earth? ,^^Choices: &&Choice1:Distance from the Sun &&Choice1:Earth's axial tilt &&Choice1:Moon's gravitational pull &&Choice1:Earth's rotation &&Choice1:Solar flares, **Answer:Earth's axial tilt>||<Question: Which celestial object is considered a dwarf planet? ,^^Choices: &&Choice1:Pluto &&Choice1:Jupiter &&Choice1:Mars &&Choice1:Venus &&Choice1:Mercury, **Answer:Pluto>||<Question: Which planet is closest to the Sun? ,^^Choices: &&Choice1:Mercury &&Choice1:Venus &&Choice1:Earth &&Choice1:Mars &&Choice1:Jupiter, **Answer:Mercury>||<Question: Why does Mercury experience extreme temperature variations? ,^^Choices: &&Choice1:It has no atmosphere &&Choice1:It is very far from the Sun &&Choice1:It rotates too slowly &&Choice1:It has many volcanoes &&Choice1:It is constantly raining, **Answer:It has no atmosphere>||<Question: How does the distance of a planet from the Sun generally affect its orbital period? ,^^Choices: &&Choice1:Closer planets have longer orbits &&Choice1:Distance does not matter &&Choice1:Closer planets have shorter orbits &&Choice1:Farthest planets rotate faster &&Choice1:All planets have the same orbital period, **Answer:Closer planets have shorter orbits>",
  created_at: new Date()
})

db.quizzes.insertOne({
  quiz_name: "test_quiz1",
  quiz_questions: "<>Question: What is the fundamental purpose of data structures?,^^Choices: &&Choice1:To make code more complex and difficult to understand &&Choice2:To organize, manage, and store data efficiently &&Choice3:To replace the need for algorithms in programming &&Choice4:To serve as passive repositories for information &&Choice5:To be the only component that determines a program's speed**Answer:Choice2:To organize, manage, and store data efficiently<>Question: The choice of an appropriate data structure can be the difference between a sluggish program and a high-performance one. This is primarily a trade-off between what two factors?,^^Choices: &&Choice1:Speed and cost &&Choice2:Time (speed of operations) and space (memory usage) &&Choice3:Complexity and readability &&Choice4:Primitive and non-primitive structures &&Choice5:Linear and non-linear relationships**Answer:Choice2:Time (speed of operations) and space (memory usage)<>Question: Which of the following is a key characteristic that distinguishes a Stack from a Queue?,^^Choices: &&Choice1:A Stack has a fixed size, while a Queue is dynamic. &&Choice2:A Stack uses indices for access, while a Queue uses nodes. &&Choice3:A Stack follows a First-In, First-Out order, while a Queue follows Last-In, First-Out. &&Choice4:A Stack follows a Last-In, First-Out order, while a Queue follows First-In, First-Out. &&Choice5:A Stack is a non-linear structure, while a Queue is linear.**Answer:Choice4:A Stack follows a Last-In, First-Out order, while a Queue follows First-In, First-Out.<>Question: A Linked List has an advantage over an Array in what area?,^^Choices: &&Choice1:Speed of access to individual elements &&Choice2:Memory usage efficiency &&Choice3:Fixed size allocation &&Choice4:Dynamic memory allocation &&Choice5:Ease of programming**Answer:Choice4:Dynamic memory allocation<>Question: Which data structure would be most appropriate for a task that requires managing data in the exact order it was received, such as handling print jobs?,^^Choices: &&Choice1:Stack &&Choice2:Array &&Choice3:Graph &&Choice4:Tree &&Choice5:Queue**Answer:Choice5:Queue<>Question: Integers and booleans are categorized as what type of data structure?,^^Choices: &&Choice1:Non-primitive structures &&Choice2:Linear structures &&Choice3:Complex structures &&Choice4:Primitive structures &&Choice5:Non-linear structures**Answer:Choice4:Primitive structures<>Question: What is the primary reason Graphs are considered indispensable?,^^Choices: &&Choice1:They enable rapid searching, insertion, and deletion. &&Choice2:They provide dynamic memory allocation. &&Choice3:They are the most efficient data structure for all tasks. &&Choice4:They are crucial for modeling real-world networks like social connections. &&Choice5:They are the fundamental building blocks provided by a programming language.**Answer:Choice4:They are crucial for modeling real-world networks like social connections.<>Question: A Binary Search Tree is particularly effective for which set of operations?,^^Choices: &&Choice1:Modeling sequential order &&Choice2:Rapid searching, insertion, and deletion &&Choice3:Managing data in a First-In, First-Out order &&Choice4:Providing instant lookups like a hash table &&Choice5:Serving as a basic building block for other structures**Answer:Choice2:Rapid searching, insertion, and deletion<>Question: What is the broader category that includes both Trees and Graphs?,^^Choices: &&Choice1:Primitive Data Structures &&Choice2:Linear Data Structures &&Choice3:Non-primitive Data Structures &&Choice4:Sequential Data Structures &&Choice5:Static Data Structures**Answer:Choice3:Non-primitive Data Structures<>Question: True understanding of data structures is not about memorization, but about what deeper skill?,^^Choices: &&Choice1:Knowing the most obscure data structures available &&Choice2:Comprehending the trade-offs to select the right tool for the job &&Choice3:Being able to program in multiple languages &&Choice4:Always choosing the data structure with the fastest operational speed &&Choice5:Avoiding the use of primitive structures whenever possible**Answer:Choice2:Comprehending the trade-offs to select the right tool for the job",
  created_at: new Date()
  })
"""

# testdata = "<>Question: What is the fundamental purpose of data structures?,^^Choices: &&Choice1:To make code more complex and difficult to understand &&Choice2:To organize, manage, and store data efficiently &&Choice3:To replace the need for algorithms in programming &&Choice4:To serve as passive repositories for information &&Choice5:To be the only component that determines a program's speed**Answer:Choice2:To organize, manage, and store data efficiently<>Question: The choice of an appropriate data structure can be the difference between a sluggish program and a high-performance one. This is primarily a trade-off between what two factors?,^^Choices: &&Choice1:Speed and cost &&Choice2:Time (speed of operations) and space (memory usage) &&Choice3:Complexity and readability &&Choice4:Primitive and non-primitive structures &&Choice5:Linear and non-linear relationships**Answer:Choice2:Time (speed of operations) and space (memory usage)<>Question: Which of the following is a key characteristic that distinguishes a Stack from a Queue?,^^Choices: &&Choice1:A Stack has a fixed size, while a Queue is dynamic. &&Choice2:A Stack uses indices for access, while a Queue uses nodes. &&Choice3:A Stack follows a First-In, First-Out order, while a Queue follows Last-In, First-Out. &&Choice4:A Stack follows a Last-In, First-Out order, while a Queue follows First-In, First-Out. &&Choice5:A Stack is a non-linear structure, while a Queue is linear.**Answer:Choice4:A Stack follows a Last-In, First-Out order, while a Queue follows First-In, First-Out.<>Question: A Linked List has an advantage over an Array in what area?,^^Choices: &&Choice1:Speed of access to individual elements &&Choice2:Memory usage efficiency &&Choice3:Fixed size allocation &&Choice4:Dynamic memory allocation &&Choice5:Ease of programming**Answer:Choice4:Dynamic memory allocation<>Question: Which data structure would be most appropriate for a task that requires managing data in the exact order it was received, such as handling print jobs?,^^Choices: &&Choice1:Stack &&Choice2:Array &&Choice3:Graph &&Choice4:Tree &&Choice5:Queue**Answer:Choice5:Queue<>Question: Integers and booleans are categorized as what type of data structure?,^^Choices: &&Choice1:Non-primitive structures &&Choice2:Linear structures &&Choice3:Complex structures &&Choice4:Primitive structures &&Choice5:Non-linear structures**Answer:Choice4:Primitive structures<>Question: What is the primary reason Graphs are considered indispensable?,^^Choices: &&Choice1:They enable rapid searching, insertion, and deletion. &&Choice2:They provide dynamic memory allocation. &&Choice3:They are the most efficient data structure for all tasks. &&Choice4:They are crucial for modeling real-world networks like social connections. &&Choice5:They are the fundamental building blocks provided by a programming language.**Answer:Choice4:They are crucial for modeling real-world networks like social connections.<>Question: A Binary Search Tree is particularly effective for which set of operations?,^^Choices: &&Choice1:Modeling sequential order &&Choice2:Rapid searching, insertion, and deletion &&Choice3:Managing data in a First-In, First-Out order &&Choice4:Providing instant lookups like a hash table &&Choice5:Serving as a basic building block for other structures**Answer:Choice2:Rapid searching, insertion, and deletion<>Question: What is the broader category that includes both Trees and Graphs?,^^Choices: &&Choice1:Primitive Data Structures &&Choice2:Linear Data Structures &&Choice3:Non-primitive Data Structures &&Choice4:Sequential Data Structures &&Choice5:Static Data Structures**Answer:Choice3:Non-primitive Data Structures<>Question: True understanding of data structures is not about memorization, but about what deeper skill?,^^Choices: &&Choice1:Knowing the most obscure data structures available &&Choice2:Comprehending the trade-offs to select the right tool for the job &&Choice3:Being able to program in multiple languages &&Choice4:Always choosing the data structure with the fastest operational speed &&Choice5:Avoiding the use of primitive structures whenever possible**Answer:Choice2:Comprehending the trade-offs to select the right tool for the job"

# Parses a quiz question input string into a dictionary.


def parse_question(input_str):
    s = input_str.strip()    

    # split question and choices
    choices_sep = "^^Choices:"
    if choices_sep not in s:
        raise ValueError("Input string missing question or Choices part")
    question_part, rest = s.split(choices_sep, 1)
    question_text = question_part.replace("Question:", "", 1).strip()
    question_text = question_text.rstrip(',') 

    # split choices and answer (answer marker is '**Answer:')
    answer_sep = "**Answer:"
    if answer_sep in rest:
        choices_part, answer_part = rest.split(answer_sep, 1)
    elif "**Answer:" in rest:
        choices_part, answer_part = rest.split("**Answer:", 1)
    else:
        raise ValueError("Input string missing Answer part")

    # parse choices using regex split on &&ChoiceN:
    raw_choices = re.split(r'&&Choice\d*:', choices_part)
    choices = [c.strip() for c in raw_choices if c.strip()]

    # normalize answer: remove optional leading 'ChoiceN:' and trailing angle
    answer = re.sub(r'^Choice\d*:\s*', '', answer_part).strip()
    answer = answer.rstrip('>')  # remove trailing > if present
    answer = answer.rstrip(',') 
    return {
        'question': question_text,
        'choices': choices,
        'answer': answer
    }

# Parses a full quiz by repeatedly calling parse_question.


def parse_quiz(AI_string, delimiter='<>'):
    questions = AI_string.split(delimiter)
    parsed_quizzes = []

    for q_str in questions:
        q_str = q_str.strip()
        if q_str:  # skip empty strings from extra delimiters
            parsed_quiz = parse_question(q_str)
            parsed_quizzes.append(parsed_quiz)

    return parsed_quizzes

# out = parse_quiz(testdata)
# print(out)
