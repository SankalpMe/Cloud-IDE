#!/usr/bin/python3
init = \
"""{
	"jsonrpc": "2.0",
	"id": 1,
	"method": "initialize",
	"params": {
		"processId" : null,
		"rootUri" : "file:///Users/sankalp/spoj",
		"capabilities": {

		}

	}
}
"""
odoc =  \
"""
{
	"jsonrpc": "2.0",
	"method": "textDocument/didOpen",
	"params": {
		"textDocument": {
			"uri":  "file:///Users/sankalp/spoj/main.cpp",
			"languageId": "cpp",
			"version": 1,
			"text": "in"
		}
	}
}
"""
comp = \
"""
{
	"jsonrpc": "2.0",
	"id": 33,
	"method": "textDocument/completion",
	"params": {
		"textDocument": {
			"uri":  "file:///Users/sankalp/spoj/main.cpp"
		},
		"position": {
			"line": 1,
			"character": 3
		}

	}
}
"""

def get_req(content):
	content = str.lstrip(str.rstrip(content))
	header = \
	f"""Content-Length: {len(content)}\r\n\r\n""" + content + "\r\n";
	return header

def write(fname, content):
	file = open(fname, "w")
	file.write(get_req(content))
	file.close()
# write("init", init)
# write("odoc", odoc)
# write("comp", comp)
#print(header[118:])