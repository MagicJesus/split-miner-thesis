import sys, os
import uuid

sys.path.insert(0, '../../src')

from flask import Flask, Response
from flask import request, send_file, send_from_directory, jsonify
from flask_cors import CORS
from directly_follows_graph import DFG
from bpmn_diagram import BPMNDiagram
from utils.create_fake_log import create_fake_log
from pm4py.objects.log.importer.xes import importer as xes_importer

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/upload", methods=['POST', 'GET'])
def process_log():
    if request.method == 'POST':
        the_log = request.files.get('file')
        file_path = "./files/" + the_log.filename
        the_log.save(file_path)

        artificial_log = request.form.get('artificial-log')
        if artificial_log == 'true':
            artificial_log = True
        else:
            artificial_log = False

        concurrency_threshold = float(request.form.get('concurrency-threshold'))
        filtering_percentile = float(request.form.get('filtering-percentile'))

        if artificial_log:
            log = create_fake_log()
        else:
            log = xes_importer.apply(file_path)

        dfg = DFG(log=log,
                  artificial_log=artificial_log,
                  concurrency_threshold=concurrency_threshold,
                  filtering_percentile_threshold=filtering_percentile)
        diagram = BPMNDiagram(dfg, dfg.concurrency_relations, artificial=artificial_log)

        for file in os.listdir("./models"):
            print(file)
            if os.path.isfile("./models/" + file):
                print("Removing")
                os.remove("./models/" + file)
        model_id = str(uuid.uuid1())
        diagram.export_as_png("./models/model" + model_id)
        diagram.export_as_xml("./models/model", model_id + ".xml")
        path = request.base_url.replace('/upload', '')
        image = path + '/display/model' + model_id + '.png'
        xml = path + '/display/model' + model_id + '.xml'

        return jsonify(image, xml)
    else:
        return 'You are getting'


@app.route('/display/<string:filename>')
def display(filename):
    return send_file('./models/' + filename)

