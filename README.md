# EvitaAI - Mobile APP
Hi! This is a group project developed by our team EvitaAI.
The goal of this mobile application is to create a virtual platform that detects phishing and malware disguised in URLs or emails using AI. Our main aim is to democratize this technology and present it to large enterprises to help people achieve their goals without worrying about data theft.

# Project Status
The project is currently in development.
I've just finished the URL scanner function.
Right now, I'm using python 3.11.9 to build the app.
The frameworks I've been working with are kivy and openai.

# Missing Content
Some files in the folder "/misc" are empty for security reasons.

# Usage
If you want to test the app, please use your own secret API key.

The app uses approximately 1000 tokens per analysis, which can make publishing, saving, and distributing results more challenging.
If you're planning to use this app for business purposes, please contact us first at henriquegasil@gmail.com.

All the frameworks can be downloaded on the terminal with "pip install kivy openai"

# Prompts
The first promt will ask the LLM to analyse the "URL" and return only one word "confiável" or "malicioso".
The second prompt will present an analysis based on the first LLM response returning a dictionary following the model:

{'reputacao': reputation of the site's host, 'justificativa': the reason behind the judgment on the first prompt, 'seguranca': security recommendations}

# License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
