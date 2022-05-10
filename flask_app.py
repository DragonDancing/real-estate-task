from flask import Flask
from flask import request, send_file
from process_sales import get_sales

app = Flask(__name__)

@app.get('/sales')
def sales_report():
    format = request.args.get('format')
    file_path = get_sales(format)

    return send_file(file_path,
                     mimetype=f'text/{format}',
                     attachment_filename=f'sales.{format}',
                     as_attachment=True)