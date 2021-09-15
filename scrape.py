from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
from bs4 import BeautifulSoup as bs
import csv 
import re
import os
import difflib

# -*- coding: utf-8 -*-
alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever|Description)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"

f = open("CluesAndAnswers.txt", "a", encoding="utf-8")


def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

def get_tossups(keyword):
    csvfile = open('questionsanswers.csv','a', encoding='utf-8')
    fields = ["Questions", "Answers"]
    f=csv.DictWriter(csvfile, fieldnames=fields)
    f.writeheader()


    driver = webdriver.Firefox()
    driver.get("https://www.quizdb.org/")
    time.sleep(5)
    search_bar = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/main/div/div[1]/div/div[1]/div[1]/div/input')
    search_bar.send_keys(keyword)
    search_bar.send_keys(Keys.RETURN)

    time.sleep(10) 
    
    def find_element_if_present(xpath):
        try:
            return driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return None

    button = find_element_if_present(xpath="/html/body/div/div/div[3]/div/main/div/div[3]/div/div[1]/div[1]/div/div[1]/div/div[2]/button")
    if button is not None:
        button.click()
        time.sleep(60)

    page_source = driver.page_source
    driver.close()
    soup = bs(page_source, "html.parser")
    questions = soup.find_all("div", class_="ui segment question-tossup-text")
    if questions == None:
        print(x + "has no entries in QuizDB. Skipping...")
        return
    answers = soup.find_all("div", "ui segment question-tossup-answer")
    questionarray = []
    answerarray = []
    for question in questions: 
        question = question.text
        question = question.split(': ', maxsplit=1)[1]

        questionarray.append(question)
        #print(question)
        # fq.writerow({"Questions": question})
    for answer in answers:
        answer = answer.text
        answer = answer.split('[', maxsplit=1)[0]
        answer = answer.split('(', maxsplit=1)[0]
        answer = answer.split('<', maxsplit=1)[0]
        answer = answer.split(': ', maxsplit=1)[1]
        answer = answer.split('Search for this answerline', maxsplit=1)[0]
        # f.writerow({"Answers": answer})
        answerarray.append(answer)

    for answer1, question1 in zip(answerarray, questionarray):
        print(answer1 + question1)
        f.writerow({"Questions": question1, "Answers": answer1})
    csvfile.close()

fr = open("topics.txt", "r")
for x in fr:
    get_tossups(x)


with open('questionsanswers.csv', encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        if row: 
            sentances = split_into_sentences(row[0])
            for sentance in sentances:
                if difflib.get_close_matches(sentance, ["Description Acceptable"]) == []:
                    f.writelines(sentance + ':' + row[1] + '\n')

os.remove("questionsanswers.csv") 