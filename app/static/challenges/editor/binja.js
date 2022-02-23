const LLIL_HEADER = [
  "; This is Binary Ninja Low Level Intermediate Language",
  "; for the binary you're trying to reproduce.",
  "",
  ""
].join('\n')

const MLIL_HEADER = [
  "; This is Binary Ninja Medium Level Intermediate Language",
  "; for the binary you're trying to reproduce.",
  "",
  ""
].join('\n')

const HLIL_HEADER = [
  "; This is Binary Ninja High Level Intermediate Language",
  "; for the binary you're trying to reproduce.",
  "",
  ""
].join('\n')

const BNIL_HEADERS = {
  'llil': LLIL_HEADER,
  'mlil': MLIL_HEADER,
  'hlil': HLIL_HEADER
}


const binja = {
  init: function() {
    bnilview = ace.edit('bnil-edit')
    bnilview.session.setMode('ace/mode/assembly_x86')
    bnilview.commands.removeCommand('find')
    bnilview.setReadOnly(true)

    const elem = document.getElementById('bnil-function')
    const names = Object.keys(bnil)
    names.sort()

    for(const name of names) {
      let opt = document.createElement('option')

      opt.value       = name
      opt.textContent = name
      elem.appendChild(opt)
    }

    // Store and display!
    editors.map['bnil-view'] = bnilview
    binja.update()
  },

  show: function(text) {
    bnilview.setValue(text, -1)
  },

  update: function() {
    const mode = document.querySelector('#bnil-mode input:checked').value
    const func = document.getElementById('bnil-function').value
    const text = BNIL_HEADERS[mode] + bnil[func][mode]

    binja.show(text)
  }
}
