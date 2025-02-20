from flask import Flask, render_template, request, jsonify
from pathlib import Path
import os

from src.databricks.labs.remorph.transpiler.transpile_engine import TranspileEngine
from src.databricks.labs.remorph.config import TranspileConfig

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():    
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    with open('samples/snowflake/snowflake_sample_1.sql', 'r') as f:
        sample_query = f.read()
    data = {
        'sample_query': sample_query,
        'query_files': files
    }
    return render_template('index.html', data=data)

@app.route('/xpile-file', methods=['POST'])
def xpile_file():
    file = request.json.get("file", "")
    output_file = "transpiled_" + file
    return jsonify({"file": output_file})

@app.route('/xpile', methods=['POST'])
def xpile():
    user_query = request.json.get("message", "")
    
    transpiler_config_path = "samples/sqlglot_config.yaml"
    engine = TranspileEngine.load_engine(Path(transpiler_config_path))
    config = TranspileConfig(
        transpiler_config_path=transpiler_config_path,
        source_dialect="snowflake",
        input_source="input",
        output_folder="output",
        error_file_path="errors",
        skip_validation=True,
        catalog_name="default",
        schema_name="defalut",
        sdk_config=None,
    )
    #status, errors = asyncio.run(do_transpile(ctx.workspace_client, engine, config))
    #status, errors = do_transpile(ctx.workspace_client, engine, config)
    errors = []

    for error in errors:
        print(str(error))

    with open('samples/snowflake/snowflake_sample_output_1.sql', 'r') as f:
        transpiled_query = f.read()

    return jsonify({"response": transpiled_query})

@app.route("/upload-file", methods=["POST"])
def upload_files():
    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    uploaded_files = request.files.getlist("files")
    saved_files = []

    for file in uploaded_files:
        if file.filename:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            saved_files.append(file.filename)

    return jsonify({"message": "Files uploaded successfully", "files": saved_files})

@app.route("/delete-file", methods=["POST"])
def delete_file():
    data = request.get_json()
    filename = data.get("filename")

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": "File deleted successfully"})
    else:
        return jsonify({"error": "File not found"}), 404


@app.route("/files", methods=["GET"])
def get_files():
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return jsonify({"files": files})

if __name__ == '__main__':
    app.run(debug=True)
