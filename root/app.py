from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
from clangd import ClangD
import subprocess
import json
app = Flask("mywww")
CORS(app)

lsp = ClangD()
init = lsp.initialize();

cfile = "file:///Users/sankalp/lsp/t.cpp"
lfile = "/Users/sankalp/lsp/t.cpp"
fileOpen =  False
fversion = 1

@app.route("/lsp/init_status")
def handle_init_stat():
	return jsonify(init)

@app.route("/lsp/bounce", methods=["POST", "GET"])
def handle_init():
	lsp.bounce()
	noti = lsp.notifis
	if(len(lsp.notifis) > 0 ):
		lsp.notifis = [lsp.notifis[-1]]
	return jsonify(noti)

@app.route("/editor/code/change", methods=["POST"])
def handle_change():
	global fversion
	file = open(lfile, "w")
	data = json.loads(request.data.decode('utf8'))

	file.write(data["text"])
	file.close()
	res = lsp.changeFile(cfile, data)
	fversion = res["version"]
	return res

@app.route("/editor/code/complete", methods=["POST"])
def handle_complete():
	data = json.loads(request.data.decode('utf8'))

	return lsp.code_complete(cfile, data)

@app.route("/editor/open", methods=["POST"])
def handle_open():
	global fversion
	global fileOpen
	if(fileOpen):
		return {"status": "done", "version": fversion}
	fversion = 1
	fileOpen = True
	data = json.loads(request.data.decode('utf8'))
	f=  open("/Users/sankalp/lsp/t.cpp", "w")
	f.write(data["content"])
	f.close()
	
	lsp.openFile(cfile,data["content"])
	return {"status": "done"}
@app.route("/code/compile", methods=["POST", "GET"])
def handle_compile():
	#call g++ compilation
	data = json.loads(request.data.decode('utf8'))
	cfin = open("/Users/sankalp/lsp/in", "w")
	cfin.write(data["cin"])
	cfin.close()

	
	res= subprocess.run(["g++", "t.cpp", "--std=c++17"],capture_output=True,  cwd="/Users/sankalp/lsp")
	if(res.returncode == 0):
		res= subprocess.run(["./a.out"], input=(data["cin"]+"\n").encode("utf8"), capture_output=True,  cwd="/Users/sankalp/lsp")

	return {"stderr": res.stderr.decode('utf8'), "stdout": res.stdout.decode('utf8')}
app.run(debug=True)