# 📘 Prefect ETL Project — README

## 🚀 Overview

This project demonstrates how to build, deploy, and orchestrate a simple ETL pipeline using **Prefect 3**.
It includes:

* A local Prefect server
* A named work pool
* A local process worker
* A project initialized with `prefect init`
* A deployment configured via `prefect.yaml`
* Flow execution triggered from the Prefect UI or CLI
* Auto-reload behavior (no need to redeploy after modifying code)

---

## 📁 Project Structure

```
etl_prefect/
│
├── main.py             # Contains the ETL flow (@flow)
├── prefect.yaml        # Prefect deployment configuration
└── README.md
```

---

## 🛠 Requirements

* Python 3.9+
* Prefect >= 3.x

Install Prefect:

```bash
pip install prefect==3.6.4
```

---

## 🖥 1. Start the Prefect Server

The Prefect server provides:

* API
* UI Dashboard
* Storage backend for flow metadata

Run:

```bash
prefect server start
```

UI available at:

```
http://127.0.0.1:4200
```

---

## 🗂 2. Create a Work Pool

A work pool defines where jobs will run:

```bash
prefect work-pool create default-agent-pool --type process
```

---

## 👷 3. Start a Worker

A worker listens for jobs coming from the work pool:

```bash
prefect worker start --pool default-agent-pool
```

You should see logs confirming it is polling for work.

---

## 📦 4. Initialize the Prefect Project

Inside your project directory:

```bash
prefect init
```

Choose the **local** storage recipe when prompted.

This creates:

* `prefect.yaml`
* `.prefect/` configuration folder

---

## ⚙️ 5. Configure `prefect.yaml`

Update the file so Prefect knows:

* Working directory
* Flow entrypoint
* Work pool name

Example:

```yaml
pull:
- prefect.deployments.steps.set_working_directory:
    directory: "D:\\DevPold\\Codes\\Python\\DataScience\\miniprojects\\etl_prefect"

deployments:
- name: sales-etl-deployment
  description: "Sales Analytics ETL - Prefect Demo"
  version: 1.0.0

  flow_name: Sales Analytics ETL - Prefect Demo
  entrypoint: "main.py:sales_etl"
  parameters: {}

  work_pool:
    name: default-agent-pool
    work_queue_name: default
    job_variables: {}
```

---

## 🚀 6. Deploy the Flow

Run:

```bash
prefect deploy
```

Prefect will:

* Detect your flow
* Register the deployment
* Display it in the UI

---

## ▶️ 7. Run the Flow

### 🔹 From the CLI

```bash
prefect deployment run "Sales Analytics ETL - Prefect Demo/sales-etl-deployment"
```

### 🔹 From the UI

* Go to **Deployments**
* Select your deployment
* Click **Run → Quick Run**

Your worker will pick it up automatically.

---

## 🔄 8. Modify the Code Without Redeploying

As long as:

* The flow file path does not change
* The `entrypoint` stays the same
* The flow name stays the same
* The worker is running

then:

> You can modify your Python code and run it again from the UI WITHOUT deploying again.

Prefect re-imports your file on every run.

---

## 📝 Example Flow (main.py)

```python
from prefect import flow, task
import pandas as pd

@task
def extract():
    print("Extracting data...")
    return pd.DataFrame({"sales": [10, 20, 30]})

@task
def transform(df):
    print("Transforming data...")
    df["sales_double"] = df["sales"] * 2
    return df

@task
def load(df):
    print("Loading data...")
    print(df)

@flow(name="Sales Analytics ETL - Prefect Demo")
def sales_etl():
    data = extract()
    processed = transform(data)
    load(processed)

if __name__ == "__main__":
    sales_etl()
```

---

## 🧪 Troubleshooting

| Issue                           | Solution                                        |
| ------------------------------- | ----------------------------------------------- |
| `No worker found for work pool` | Ensure worker is running with correct pool name |
| Deployment not visible          | Run `prefect deploy` again                      |
| Flow not updating               | Code changes require re-run, NOT redeploy       |

---

## 📚 Resources

* Prefect Docs: [https://docs.prefect.io](https://docs.prefect.io)
* Prefect UI: [http://127.0.0.1:4200](http://127.0.0.1:4200)

