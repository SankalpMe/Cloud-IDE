import {basicSetup, EditorView} from "codemirror"
import {keymap} from "@codemirror/view"
import {EditorState, Compartment, Prec} from "@codemirror/state"
import {cpp, cppLanguage} from "@codemirror/lang-cpp"
import {defaultKeymap} from "@codemirror/commands"
import {postJSON} from './utils.js'
import {syntaxTree} from "@codemirror/language"
import {linter, Diagnostic, lintGutter} from "@codemirror/lint"

let language = new Compartment, tabSize = new Compartment

let dcode = "//Your Code...\n"
if(localStorage.getItem("code")){
  dcode = localStorage.getItem("code")
}

let cikd = ["text", "method", "function", "constructor", "field", "Variable", "Class", "Interface", "Module", "Property", "Unit", "Value", "Enum","Keyword", "Snippet","Color", "File",
"Reference", "Folder", "EnumMember", "Constant", "Struct", " Event", "Operator", "TypeParameter"]

let gikd = ["error", "warning", "info", "info"]
async function myCompletions(context) {
  let word = context.matchBefore(/\w*/)
  if (word.from == word.to && !context.explicit)
    return null
  let offset = context.state.selection.main.from
  let line = context.state.doc.lineAt(offset)
  // console.log(line.number-1, offset-line.from)

  let res = await postJSON("editor/code/complete",{"line":line.number-1, "character": offset-line.from} );
  let ores = res["result"]["items"].sort((a,b)=>a["sortText"] < b["sortText"]).map(function(ea) {
                    return {label: ea.label, apply: ea.insertText, type: cikd[ parseInt(ea.kind) -1].toLowerCase()}
                })

  return {
    from: word.from,
    options:
      ores
  }
  // return {
  //   from: word.from,
  //   options: [
  //     {label: "match", type: "keyword"},
  //     {label: "hello", type: "variable", info: "(World)"},
  //     {label: "magic", type: "text", apply: "⠁⭒*.✩.*⭒⠁", detail: "macro"}
  //   ]
  // }
}

var latest = []
let version = -1;
let clangLinter = linter(async (view) => {
  console.log(view.state.doc.toString())
  let diagnostics = []
  async function generateLints(){
    let res = await postJSON("lsp/bounce");

    if(res.length > 0){
      console.log(res[res.length-1].params.version, version)
      if(res[res.length-1].params.version == version){
        latest = res[res.length-1].params.diagnostics
      }
      else{
        if(version != -1){
          await new Promise(r => setTimeout(r, 500));
          return generateLints()
        }
        
      }

    }

  };

  await generateLints();
  
  diagnostics = latest.map((elem)=>{
    function flatten(pos){
      return view.state.doc.line(pos.line+1).from + pos.character
    }


    return {
      from: flatten(elem.range.start),
      to: flatten(elem.range.end),
      severity: gikd[elem.severity-1],
      message: elem.message,
      actions: []
    }

  })

  return diagnostics
})


const gvc = cppLanguage.data.of({
  autocomplete: myCompletions
})

let state = EditorState.create({
  doc: dcode,
   extensions: [   basicSetup, cpp(), gvc, lintGutter() , EditorState.changeFilter.of((effect)=>{
 
    if(effect.annotations.length > 0){
      let atype = String(effect.annotations[0].value)
      if(atype.indexOf("input") > -1 || atype.indexOf("delete") > -1){
         let bval = effect.state.doc.toString();
         postJSON('editor/code/change',{'text': bval}).then((data)=>{
          version = data.version
         })
         localStorage.setItem("code", bval);
      }
      
    }
    return true
   }), clangLinter],
})


//let transaction = state.update({changes: [{from: 0, insert: "0"},{from: 0, insert: "1"}] })
// console.log(transaction.state.doc.toString())

let view = new EditorView({
  state,

  parent: document.getElementById("editor")
})




async function init(){
	let res = await postJSON("editor/open",{content: state.doc.toString()});
	version = res.version
  return "done"
}

init()
let cbtn = document.getElementById("compileBtn")
let cview = document.getElementById("compileOut")
let cin = document.getElementById("cin")
cbtn.addEventListener("click",async function(){
  cbtn.disabled = true;
  let otext = cbtn.innerText
  cbtn.innerText = "Compiling...."
  cview.innerText = ''
  let res = await postJSON("code/compile", {'cin': cin.value})

  cview.innerText = "STDOUT:\n" + res.stdout+"\n------\nSTDERR:\n"+res.stderr
  cbtn.disabled = false;
  cbtn.innerText = otext
})