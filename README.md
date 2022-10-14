### Description
Select_candidate_api is the backend side of the project select candidate. The frontend side is available [here](https://github.com/iamklaus01/select_candidates_frontEnd). This project is made with constraint programming for automating candidates selection process by permitting to user to define his own criteria to pply to each candidate.

### Installation
- Clone the GitHub repository. Don't forget to clone the frontend repository too.

    - `git clone https://github.com/iamklaus01/select_candidates_frontEnd` <br>
    - `cd select_candidates_frontEnd`

- Install all packages required findable in requirements.txt file
- Create pgsql database named selectd
- Update this line in `database.py` file `DATABASE_URL = "postgresql://{username}:{password}@localhost/selectd"`

### Usage

- Activate your environment if you're using one 
- Run command `uvicorn main:app --reload`
- Go to http://127.0.0.1:8000/docs for interact with the api without frontend side


### License
All rights reserved.