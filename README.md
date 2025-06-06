# EvitaAI - Android APP
Hi! This is a group project developed by our team EvitaAI.
The goal of this mobile application is to create a virtual platform that detects phishing and malware disguised in URLs using AI. Our main aim is to democratize this technology and present it to large enterprises to help people achieve their goals without worrying about data theft.

# Project Status
The project is almost finished.
I'm currently testing the app on android and fixing issues on the android, but the app is ready.
Right now, I'm using python 3.10 to build the app.
The frameworks I've been working with are avaible on [requirements](./requirements.txt).
I'm building the APK with buildozer and pyjnius on Ubuntu 22.04.5 LTS - WSL2 (Windows Subsystem for Linux 2).

# Missing Content
Some json files in the folder "/misc" are empty for security reasons.

# Missing Permissions
The latest Android system has become quite strict regarding the permissions requested by apps. Currently, you need a license or must publish the app on the Google Play Store to use certain permissions.

# Usage
If you want to test the app, please use your own secret API key.

The app uses approximately 1200 tokens per analysis, which can make publishing, saving, and distributing results more challenging.
If you're planning to use this app for business purposes, please contact us first at henriquegasil@gmail.com.

After creating a virtual env, chose the requirements file to download all libraries if you want to open the app on computer.

If you want to build the app, open the Ubuntu terminal, find the app folder with:

 cd path/

and start the process with:

  buildozer android debug

it will create two folders: 
/.buildozer and /bin
the APK will be in the /bin folder

# Prompts
The first promt will ask the LLM to analyse the "URL" and return only one word "confiável" or "malicioso".
The second prompt will present an analysis based on the first LLM response returning a dictionary following the model:

{'reputacao': reputation of the site's host, 'justificativa': the reason behind the judgment on the first prompt, 'seguranca': security recommendations}

# License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
