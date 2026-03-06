# SMConstruct (Sentence Mining Construct)

**Pre-Release** </br>
A tool for users to easily translate and mine sentences from transcripts for language learning.

## Description

Watch your favorite youtube videos for language learning. The goal of this project is to make sentence mining easier and more accessable for language learning. By having the translation model integrated locally we are able to trade the cost assosiated using llm tokens for running it on hardware.

## Features

- Integration with Anki
- Local LLM integration.
- Translate single words or phrases throughout a transcript.
- Capture video frame and audio to your flashcards.

## Getting Started

## Dependencies

### Installing Locally
* Python 3.12
* Node.js / npm

### Installing with Docker
* Docker

## Installing

### Running Natively (Windows Only)

Pull the repo from Github and navigate to the folder.
```
cd SMConstruct
```

Run the setup.py script in the root folder. This will install further dependencies.

```
python3 setup.py
```

This will generate a `start.bat` and a `stop.bat` in the root folder. Now you can use these to start and stop the program.
```
...
- start.bat
- stop.bat
```


### Installing with Docker
After Docker is installed navigate to the SMTK folder.
```
cd SMConstruct
```

Build and run the container

```
docker-compose up --build 
```

* Note *
This can take a while as we need to pull the model from hugging face. (~ 4gb)

<!-- 
It spans multiple lines and is not rendered in the final output. 

[![Watch the video](https://img.youtube.com/vi/a5O-t6E_FVI/maxresdefault.jpg)](https://youtu.be/a5O-t6E_FVI)

### [Watch this video on YouTube](https://youtu.be/a5O-t6E_FVI)
-->

## Currently Working on
- Fixing bugs / errors.
- UI / UX fixes.
- Better card customization.
- Further Optimizations.
- Easier Installation.

## Authors

Contributors names and contact info

Logan Fani  
Email: [logancfani@gmail.com](logancfani@gmail.com)

## Version History

* 0.1
    * Initial Pre-Release and testing phase.

## License

This project is licensed under the MIT License - see the LICENSE file for details
