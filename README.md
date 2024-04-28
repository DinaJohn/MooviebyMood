# Template for ECS639U Group Coursework

This repository contains the code for the web app 'Moovie by Mood', along with the code for the feedback predictor, simulator and evaluation results. Please look at the below instruction to run the website on your local browser (preferbally google chrome). I've also mentioned what each folder in the repository comprises off for easy navigation and clarity.

## Local development

To run this project in your development machine, follow these steps:
1. Download the projetc zip folder from Github. You can do this by clicking on the green box 'Code'.

1. If you dont have miniconda installed on your system, please download it from: https://docs.anaconda.com/free/miniconda/
   Once you've installed miniconda, please create a virtual environment to run django. Follow the below steps on terminal:
    ```console
        $ conda create --name movie_env python=3.10
    ```
    ```console
        $ conda activate ECS639U
    ```
    ```console
        $ pip install django
    ```

4. Install Pyhton dependencies (main folder):

    ```console
    $ pip install -r requirements.txt
    ```
    Please be sure to run this command in the main folder of downloaded zip file.


7. If everything is alright, you should be able to start the Django server from the main folder:

    ```console
    $ python manage.py runserver
    ```

9. Open your browser and go to http://localhost:8000, you will be greeted with a template page.
