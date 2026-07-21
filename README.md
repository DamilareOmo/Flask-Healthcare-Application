# Flask Healthcare Application
# Household Income & Spending Survey

A Flask + MongoDB survey tool that collects respondents' age, gender, total
income, and category-level expenses (utilities, entertainment, school fees,
shopping, healthcare), then processes the results into a CSV, analyzes them
in a Jupyter notebook, and exports client-ready charts and a PowerPoint deck
— built ahead of a new healthcare product launch.

## Project structure

```
survey_project/
├── app.py                      # Flask web app (form + MongoDB storage)
├── config.py                   # Env-driven configuration (Mongo URI, Flask settings)
├── models/
│   └── user.py                 # User class used to process each survey record
├── export_to_csv.py            # Loops through MongoDB, writes data/survey_export.csv
├── generate_pptx.py            # Assembles notebook charts into a client .pptx
├── notebook/
│   └── analysis.ipynb          # Loads the CSV, produces the required visualizations
├── scripts/
│   ├── build_notebook.py       # Regenerates analysis.ipynb from source (optional)
│   └── seed_sample_data.py     # Inserts random sample responses for testing/demo
├── templates/index.html        # Survey form
├── static/style.css            # Form styling
├── data/                       # CSV export, generated charts, and .pptx land here
├── requirements.txt
├── Dockerfile                  # For containerized AWS deployment
├── .env.example                # Copy to .env and fill in your own values
└── README.md
```

## 1. Local setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit .env with your MongoDB URI, etc.
```

### MongoDB options

The app is fully configurable via environment variables in `.env` — no code
changes needed for any of these:

- **Local MongoDB**: install MongoDB Community Server, run `mongod`, and keep
  the default `MONGO_URI=mongodb://localhost:27017`.
- **MongoDB Atlas (free tier)**: create a cluster at
  [mongodb.com/atlas](https://www.mongodb.com/atlas), get your connection
  string, and set `MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net`.
- **Docker**: `docker run -d -p 27017:27017 --name survey-mongo mongo:7`

### Run the app

```bash
python app.py
```

Visit `http://localhost:5000`, fill out the form, and submit a few test
responses. Each submission is stored as a MongoDB document with this shape:

```json
{
  "age": 34,
  "gender": "female",
  "total_income": 4200.0,
  "expenses": {
    "utilities": 180.0,
    "entertainment": 0.0,
    "school_fees": 0.0,
    "shopping": 220.0,
    "healthcare": 95.0
  },
  "submitted_at": "2026-07-18T09:00:00Z"
}
```

### No real responses yet? Seed sample data

```bash
python scripts/seed_sample_data.py --count 150
```

## 2. Export to CSV

```bash
python export_to_csv.py
```

This connects to MongoDB, wraps every document in a `User` object
(`models/user.py`), and writes `data/survey_export.csv` with one row per
respondent (age, gender, income, per-category expenses, total expenses,
and savings).

## 3. Analyze in Jupyter

```bash
jupyter notebook notebook/analysis.ipynb
```

Run all cells. The notebook:

1. Loads `data/survey_export.csv`
2. Charts the ages with the highest average income
3. Charts gender distribution across each spending category
4. Adds a bonus income-vs-expenses view for context
5. Saves each chart as a PNG to `data/charts/`

If you edit the notebook's source instead of the `.ipynb` directly, regenerate
it with `python scripts/build_notebook.py`.

## 4. Build the client PowerPoint

```bash
python generate_pptx.py
```

Assembles the exported PNG charts into `data/client_presentation.pptx` —
a title slide plus one slide per chart, ready to share with the client.

## 5. Deploy to AWS

Two common paths — pick whichever fits your team's setup.

### Option A: AWS Elastic Beanstalk (simplest)

1. Install the EB CLI: `pip install awsebcli`
2. From the project root:
   ```bash
   eb init -p docker survey-app --region us-east-1
   eb create survey-env
   ```
3. Set your environment variables (instead of uploading `.env`):
   ```bash
   eb setenv MONGO_URI="mongodb+srv://..." MONGO_DB_NAME=survey_db \
             MONGO_COLLECTION=responses FLASK_SECRET_KEY="<random-string>"
   ```
4. `eb deploy` to push updates. `eb open` to view the live URL.

### Option B: EC2 + Docker

1. Launch an EC2 instance (Amazon Linux 2023, t3.micro is enough for a demo).
2. Install Docker:
   ```bash
   sudo yum update -y && sudo yum install -y docker
   sudo systemctl start docker && sudo usermod -aG docker ec2-user
   ```
3. Copy the project to the instance (`scp` or `git clone`), then:
   ```bash
   docker build -t survey-app .
   docker run -d -p 80:5000 --env-file .env --name survey-app survey-app
   ```
4. Open port 80 in the instance's security group.
5. Point MongoDB to Atlas (recommended) so the database survives instance
   restarts, or attach an EBS volume if running MongoDB on the same box.

### Notes for either option

- Never commit `.env` — set secrets through `eb setenv`, EC2 environment
  variables, or AWS Secrets Manager instead.
- The `/health` endpoint (`GET /health`) checks MongoDB connectivity and is
  wired up for load balancer health checks.
- `gunicorn` (already in `requirements.txt`) serves the app in production;
  the Dockerfile is already configured to use it instead of Flask's dev server.

## Data flow summary

```
Flask form  --insert-->  MongoDB
                            |
                     export_to_csv.py
                            |
                     data/survey_export.csv
                            |
                    notebook/analysis.ipynb
                            |
                     data/charts/*.png
                            |
                     generate_pptx.py
                            |
              data/client_presentation.pptx
```
