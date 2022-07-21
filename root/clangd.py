import subprocess
import command
from time import sleep, time
import json
import select
v = 1
def pjson(data):
	print(json.dumps(data, indent=1))
def rpc_request(req, id):
	req["id"] = id
	req["jsonrpc"] = "2.0"
	return command.get_req(json.dumps(req))

def rpc_notify(req):
	req["jsonrpc"] = "2.0"
	return command.get_req(json.dumps(req))
inBounce = False
class ClangD:
	def __init__(self):
		self.file = open("out.txt", "w")
		self.proc = subprocess.Popen("clangd", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
		self.reqResponse = dict()
		self.notifis = []
		self.poll_obj = select.poll()
		self.poll_obj.register(self.proc.stdout, select.POLLIN)
	def initialize(self):
		init_req = {
			"method": "initialize",
			"params": {
				"processId" : None,
				"rootUri" : "file:///Users/sankalp/lsp",
				"capabilities": {
					"textDocument": {
						"completion": {
							"completionItem":{
								"insertReplaceSupport": True
							}
						}
					}
				}
			}
		}

		return self.handle_request(init_req)
	def handle_request(self, req):
		req_id = "my"+str(time())
		req = rpc_request(req, req_id)
		self.writeData(req)
		while not req_id in self.reqResponse:
			self.bounce()
		resp = self.reqResponse[req_id]
		del self.reqResponse[req_id]
		return  resp

	def handle_notify(self, notif):
		reqNotif = rpc_notify(notif)
		self.writeData(reqNotif)
		self.bounce()

	def bounce(self):
		global inBounce
		if(inBounce):
			return
		inBounce = True
		poll_result = self.poll_obj.poll(0)
		if poll_result:
			resp = self.pollData()
			if "id" in resp:
				self.reqResponse[resp["id"]] = resp
			else:
				self.notifis.append(resp)
		inBounce = False

	def openFile(self, fileURI, text, version=1):
		odoc =  {
			"method": "textDocument/didOpen",
			"params": {
				"textDocument": {
					"uri":  fileURI,
					"languageId": "cpp",
					"version": version,
					"text": text
				}
			}
		}
		self.handle_notify(odoc)
		
	def changeFile(self, fileURI, data):

		ver = int(time())
		print("VERSION:",ver)
		rdoc  =  {
			"method": "textDocument/didChange",
			"params": {
				"textDocument": {
					"version": ver,
					"uri":  fileURI
				},
				"contentChanges": [data]
			}
		}
		
		self.handle_notify(rdoc)
		return {"version" : ver}

	def code_complete(self, fileURI, pos):

		occ = {
			"method": "textDocument/completion",
			"params": {
				"textDocument": {
					"uri":  fileURI
				},
				"position": pos
			}


		}

		
		return self.handle_request(occ)

	def writeData(self, data):
		self.proc.stdin.write(data.encode('utf8'))
		self.proc.stdin.flush()


	def pollData(self):
		line = self.proc.stdout.readline().decode('utf8')
		
		if "Content-Length:" in line:
			cl = int(str.strip((line).split(":")[-1]))
			
			data = self.proc.stdout.read(cl+2).decode('utf8')
		
			return json.loads(data)
		
# a = ClangD()
# sleep(1)
# a.initialize()
# sleep(2)
# a.openFile("file:///Users/sankalp/lsp/t.cpp","abcd")
# sleep(10)