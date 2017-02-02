#!/usr/bin/python
import praw
import pdb
import re
import os
import requests
from google import search
from bs4    import BeautifulSoup


SUBREDDITNAME = 'geartrade'
botMessage = "\n\n" + "*****" + "\n\n" + "^I'm ^a ^bot, ^and ^I've ^done ^my ^best ^to ^find ^your ^item ^on ^backcountry.com ^and ^provide ^the ^lowest ^listed ^selling ^price ^your ^reference." + "\n\n" + "^It's ^possible ^that ^I ^may ^have ^chosen ^the ^wrong ^item. ^Feel ^free ^to ^send ^me ^a ^PM ^to ^report ^any ^sort ^of ^feedback." + "\n\n" + "^I ^was ^created ^by ^u/WarDEagle."


def between_i(string, start='', end=''):
    """
        Iteratively find all string wrapped by start and end within a string.
        """
    # Used to store the results
    result = []
    
    # Iterate until there's no string found
    while True:
        # If no start is specified, start at the beginning
        if not start:
            s = 0
        # Else find the first occurrence of start
        else:
            s = string.find(start)
        # If end is empty, end at the ending
        if not end:
            e = len(string)
        # Else find the first occurrence of end
        else:
            e = string.find(end)
        # Base case, if can't find one of the element, stop the iteration
        if s < 0 or e < 0:
            break
        # Append the result
        result.append(string[s+len(start):e])
        # Cut the string
        string = string[e+len(end):]
    return result



def hasValidTag(tag):
    tagLower = tag.lower()
    if "wtb" in tagLower:
        return False
    elif "[" not in tag or "]" not in tag:
        return False
    else:
        return True



def notRei(title):
    titleLower = title.lower()
    if "rei" in titleLower:
        return False
    else:
        return True



def match(titleIn):
    # get matching url from google
    keywords = titleIn[5:].split(' ') # stores keywords from title
    results  = [] # stores urls with matching keywords
    searchTitle = "site:backcountry.com " + titleIn[5:] # chops off "[WTS] - " tag
    urls = search(searchTitle, stop=10) # stores google result urls
    print titleIn[5:]
    
    for url in urls:
        # try to get the urls, but catch exceptions from encoding errors
        try:
            urlStr = url.encode('utf8')
        except:
            return "No results found."
        
        mismatches = 0
        urlKeywords = urlStr[27:].split('-')
        if mismatches < 5:
            results.append(url)

    if len(results) > 0 and hasValidTag(titleIn[:5]) and notRei(titleIn):
        res = requests.get(results[0])
        html = res.content
        lowPrices  = between_i(html, "\"lowSalePrice\":\"", "\",")
        # clean up array
        i = 0
        while i < len(lowPrices):
            if lowPrices[i] == "":
                lowPrices.pop(i)
            else:
                i += 1
        # get lowest of all listed prices
        lowPrices.sort()
        if len(lowPrices) > 0:
            priceMessage = "Currently, the lowest price for this item on [backcountry.com](" + results[0] + ") is " + lowPrices[0] + "." + botMessage
            return priceMessage
        else:
            return "No results found."
    else:
        return "No results found."



def main() :
    # Create the Reddit instance
    reddit = praw.Reddit('bot1')

    # Have we run this code before? If not, create an empty list
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []

    # If we have run the code before, load the list of posts we have replied to
    else:
        # Read the file into a list and remove any empty values
        with open("posts_replied_to.txt", "r") as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    # Get the stream of new submissions from the subreddit
    subreddit = reddit.subreddit(SUBREDDITNAME)
    for submission in subreddit.stream.submissions():
        submissiontitle = submission.title
        
        # If we haven't replied to this post before
        if submission.id not in posts_replied_to:
        
            message = match(submissiontitle)
            if message != "No results found.":
                submission.reply(message)
                print "Submission to " + submission.title + ": " + message
            else:
                print "No results found. No submission made."
            
            # Store the current id into our list
            posts_replied_to.append(submission.id)

    # Write our updated list back to the file
    with open("posts_replied_to.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")



# call main if this script is being exe'd
if __name__ == '__main__':
    main()