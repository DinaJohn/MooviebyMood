# Moovie by Mood

This repository contains the code for the web app 'Moovie by Mood', along with the code for the feedback predictor, simulator and evaluation results. Please look at the below instruction to run the website on your local browser (preferbally google chrome). I've also mentioned what main folders in the repository comprises off for easy navigation and clarity. Additionally, login username and password for 5 users have beeen metioned below.

## Opening the Web App on your Local Device

To run this project in your development machine, follow these steps:

1. If you dont have miniconda installed on your system, please download it from: https://docs.anaconda.com/free/miniconda/
   Once you've installed miniconda, please create a virtual environment to run django. Follow the below steps on terminal:
    ```console
    $ conda create --name movie_env python=3.10
    ```
    ```console
    $ conda activate movie_env
    ```
2. Download the project zip folder from Github. You can do this by clicking on the green box 'Code'. Alternatively, you could clone the repository to your local machine.
   ```console
   git clone https://github.com/DinaJohn/MoviebyMood.git
   ```
3. Install Python dependencies (main folder):

    ```console
    $ pip install -r requirements.txt
    ```
    Please be sure to run this command in the main folder of the downloaded zip file.


4. If everything is set, you should be able to start the Django server from the main folder:

    ```console
    $ python manage.py runserver
    ```

5. Open your browser and go to http://localhost:8000. You should be able to view and use the web app.

## Login Details:

Please use the below details to login to the web app:

| Username  | Password |
| ------------- | ------------- |
| 1  | Hello123  |
| 2  | Hello124  |
| 3  | Hello125  |
| 4  | Hello126  |
| 5  | Hello127  |

## File Directory:

-> api - Django folder where you can find all the code related to the backend and recommendation system. Recommend_function.py is the main file for all code regarding the recomendation systems.

-> frontend - Vue folder where you can find all code realated to the frontend.

-> The jupyter notebooks for the feedback predictor, simulation and results of the simulation is present. The .csv files containing the simulation results is also attached for reference.

-> best_model.joblib is the saved model of feedback predictor.
