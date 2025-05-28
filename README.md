# EvitaAI - Mobile APP
Hi! This is a group project developed by our team EvitaAI.
The goal of this mobile application is to create a virtual platform that detects phishing and malware disguised in URLs or emails using AI. Our main aim is to democratize this technology and present it to large enterprises to help people achieve their goals without worrying about data theft.

# Project Status
The project is currently in development.
Right now, I'm using python 3.11.9 to build the app.
The frameworks I've been working with are kivy and openai.

  pip install kivy openai

# Missing files
Some miscellaneous files have not been uploaded for security reasons.
If you want to test the app, please use your own secret API key.

# Important

When writing your own promt, you must follow the template bellow for the output:
  '''
  Topic1 = Is the site reliable or malicious? (answear only with one word) \n/////\n
  Topic2 = What can you tell me about the domain of the site? \n/////\n
  Topic3 = Justify the info you gave me in Topic1. \n/////\n
  Topic4 = Recommend me security measures.
  '''
Note the pattern "\n/////\n" - it’s used to split the string output by the LLM.

# Usage
The app uses approximately 1000 tokens per analysis, which can make publishing, saving, and distributing results more challenging.
If you're planning to use this app for business purposes, please contact us first at henriquegasil@gmail.com.

# License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
