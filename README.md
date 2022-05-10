# real-estate-task

## Install

- Install dependcies
  
    ```bash
    pip install -r requirements.txt
    ```

- Download and unzip 'input' folder from [this link](https://drive.google.com/drive/folders/1dw7EV9WaYRsb5I7eTJbnRLexWEB-JKkw?usp=sharing) and place it in the root folder

- run flask
    ```bash
    flask run
    ```

## REST API

There's only GET endpoint with one `format` parameter. It's `csv` by default and can be changed to `parquet`.
It will generate file in the `output` directory.

### Request

`GET /sales?format=[csv,parquet]`

Two available requests
```
http://localhost:5000/sales?format=csv
http://localhost:5000/sales?format=parquet
```

Download via `curl`
```
    curl http://localhost:5000/sales?format=csv -o sales.csv
    curl http://localhost:5000/sales?format=parquet -o sales.parquet
```