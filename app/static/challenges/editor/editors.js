const NO_COMP = "The compiler didn't produce any output."

const DIFF_HEADER = [
  "; Lines beginning with - (yellow) occur in your binary, but not the target.",
  "; Lines beginning with + (purple) occur in the target binary, but not yours.",
  "; Sections with pale highlighting differ only in their operands.",
  "",
  ""
].join('\n')

const TARGET_HEADER = [
  "; This is the disassembly you're trying to reproduce.",
  "; It uses Intel syntax (mov dst, src).",
  "",
  ""
].join('\n')

const CANDIDATE_HEADER = [
  "; This is the disassembly of your most recent submission.",
  "; It uses Intel syntax (mov dst, src).",
  "",
  ""
].join('\n')


const editors = {
  disasm_marker: null,
  source_marker: null,
  source_map: new Map(),
  modified: false,

  init: function() {
    codeedit = ace.edit('code-edit')
    switch(language) {
      case 'c':
      case 'cpp':
        codeedit.session.setMode('ace/mode/c_cpp')
        break
      case 'go':
        codeedit.session.setMode('ace/mode/golang')
        break
      case 'nim':
        codeedit.session.setMode('ace/mode/nim')
        break
      case 'rust':
        codeedit.session.setMode('ace/mode/rust')
        break
      case 'swift':
        codeedit.session.setMode('ace/mode/swift')
        break
      default:
        console.warn('No highlighter for language: ' + language)
        codeedit.session.setMode('ace/mode/text')
        break
    }

    codeedit.session.setOptions({
      useSoftTabs: true,
      tabSize: 2
    })

    codeedit.commands.removeCommand('find')
    codeedit.commands.addCommand({
      name: 'compile',
      bindKey: {win: 'Ctrl-Enter', mac: 'Command-Enter'},
      exec: () => buttons.compile()
    })

    codeedit.commands.addCommand({
      name: 'replace',
      bindKey: {win: 'Ctrl-H', mac: 'Command-H'},
      exec: () => replace.open()
    })

    compview = ace.edit('comp-view')
    compview.commands.removeCommand('find')
    compview.setReadOnly(true)

    diffview = ace.edit('asm-edit')
    diffview.session.setMode('ace/mode/assembly_x86')
    diffview.setReadOnly(true)
    diffview.commands.addCommand({
      name: 'find',
      bindKey: {win: 'Ctrl-F', mac: 'Command-F'},
      exec: () => find.open(),
      readOnly: true
    })

    diffview.on('changeSelection', function() {
      diffview.session.removeMarker(editors.disasm_marker)
      codeedit.session.removeMarker(editors.source_marker)

      let sel   = diffview.session.getSelection()
      let line  = sel.cursor.row
      let text  = diffview.session.getLine(line)
      let range = editors.source_map.get(line)

      if(range !== undefined) {
        let asmrange = new ace.Range(line, text.search(/[^-+ ]|$/), line, text.length)
        editors.disasm_marker  = diffview.session.addMarker(asmrange, 'ace_step srcmap', 'text')
        editors.source_marker  = codeedit.session.addMarker(   range, 'ace_step srcmap', 'text')
      }
    })

    // Ask for confirmation if the user leaves before compiling:
    codeedit.session.on('change', e => {editors.modified = true})
    window.onbeforeunload = function() {
      if(editors.modified) return 'Compile to save your code changes.'
    }

    editors.map = {
      'code-edit': codeedit,
      'comp-view': compview,
      'diff-view': diffview
    }

    // Init the function selector
    editors.functions(target)
  },

  clear_code_markers: function() {
    // Remove the compiler notes from the source view
    codeedit.session.setAnnotations([])
  },

  clear_diff_markers: function() {
    // Remove the colored banding from the diff view
    for(const id in diffview.session.getMarkers()) {
      diffview.session.removeMarker(id)
    }
  },

  clear_source_map: function() {
    // Remove the source map scaffolding
    editors.source_map.forEach(function(range) {
      range.start.detach()
      range.end.detach()
    })

    editors.source_map.clear()
  },

  candidate: function(name) {
    let text = ''
    for(const hunk of candidate.functions[name].hunks) {
      if(hunk[0] != 1) text += hunk[1]
    }

    return text
  },

  code: function(decomp) {
    // Reset the user's candidate source code
    editors.clear_code_markers()
    editors.clear_diff_markers()
    editors.clear_source_map()

    codeedit.setValue(decomp, -1)
    compview.setValue("Compile to see compiler output.", -1)
    diffview.setValue("; Compile to see the disassembly diff.", -1)

    document.getElementById('score-ins').textContent = '-?'
    document.getElementById('score-del').textContent = '+?'
  },

  comp: function(stdout) {
    // Set the console output
    let codemarkers = notices.auto(stdout)
    codeedit.session.setAnnotations(codemarkers)
    compview.setValue(stdout || NO_COMP, -1)
  },

  diff: function(tgt, cdt) {
    let dmp = new diff_match_patch()
    let a = dmp.diff_linesToChars_(cdt, tgt)
    let hunks = dmp.diff_main(a.chars1, a.chars2, false)

    for(const hunk of hunks) {
      hunk.push(hunk[1].length)
    }

    dmp.diff_charsToLines_(hunks, a.lineArray)
    // dmp.diff_cleanupSemantic(hunks)
    return hunks
  },

  functions: function(fninfo) {
    const elem = document.getElementById('asm-function')
    const func = elem.value || Object.keys(fninfo)[0]

    while(elem.firstChild) {
      elem.removeChild(elem.firstChild)
    }

    const names = Object.keys(fninfo)
    names.sort()

    for(const name of names) {
      let opt  = document.createElement('option')
      let text = name

      if(text.length > 50) {
        // Damn you, std::mersenne_twister_engine!
        text = text.slice(0, 48) + '...'
      }

      if(fninfo[name].delta) {
        let ins = fninfo[name].delta[0]
        let del = fninfo[name].delta[2]
        text += ` (-${ins}/+${del})`
      }

      opt.value = name
      opt.textContent = text
      elem.appendChild(opt)
    }

    elem.value = func
    editors.update()
  },

  replace: function(text, which) {
    for(const tr of document.getElementById('replacements').children) {
      const src = tr.children[1].children[0].value
      const wch = tr.children[3].children[0].value
      const dst = tr.children[5].children[0].value

      if(src && wch === which) {
        text = text.replaceAll(src, dst)
      }
    }

    return text
  },

  showDiff: function(hunks, srcmap) {
    // Show a diff in the ASM tab
    editors.clear_diff_markers()
    editors.clear_source_map()

    // Find "minor" diffs for paler highlighting:
    const opregex = /^(block|  \w+).*$/gm
    for(let i = 1; i < hunks.length; ++i) {
      let a = hunks[i - 1]
      let b = hunks[i]

      // Skip mismatched types and lengths:
      if(a[0] !== -b[0]) continue
      if(a[2] !==  b[2]) continue

      // Compare the operations ignoring operands:
      let aaa = a[1].replace(opregex, (m, op) => op)
      let bbb = b[1].replace(opregex, (m, op) => op)
      if(aaa === bbb) {
        a.push('minor')
        b.push('minor')
        i += 1
      }
    }

    let smline = 0
    let lineno = 4
    let prefix = ['-', ' ', '+']
    let header = DIFF_HEADER

    diffview.setValue(header + hunks.flatMap(diff => {
      const style = diff[0] // -1 = extra; 0 = common; 1 = missing
      const text  = diff[1]
      const lines = diff[2]

      if(style !== 0) {
        let minor = (diff[3] === 'minor')? ' minor' : ''
        let range = new ace.Range(lineno, 1, lineno + lines - 1, 2)
        let klass = ['diff-del', null, 'diff-ins'][style + 1] + ' line-marker' + minor
        diffview.session.addMarker(range, klass, 'line', false)
      }

      return text.trimEnd().split('\n').map(line => {
        if(srcmap && style !== 1) {
          let range   = new ace.Range()
          let line    = srcmap[smline] - 1
          let text    = codeedit.session.getLine(line)
          range.start = codeedit.session.doc.createAnchor(line, text.search(/\S|$/))
          range.end   = codeedit.session.doc.createAnchor(line, text.length)
          editors.source_map.set(lineno, range)
          smline += 1
        }

        lineno += 1
        return prefix[style + 1] + line
      })
    }).join('\n'), -1)
  },

  showText: function(text, srcmap) {
    // Show plain assembly in the ASM tab
    editors.clear_diff_markers()
    editors.clear_source_map()

    diffview.setValue(text, -1)
    if(!srcmap) return

    for(let i = 0; i < srcmap.length; ++i) {
      if(!srcmap[i]) continue

      let range   = new ace.Range()
      let line    = srcmap[i] - 1
      let text    = codeedit.session.getLine(line)
      range.start = codeedit.session.doc.createAnchor(line, text.search(/\S|$/))
      range.end   = codeedit.session.doc.createAnchor(line, text.length)
      editors.source_map.set(i + 3, range)
    }
  },

  target: function(name) {
    const info = target[name]
    return (info)? info.asm : ''
  },

  update: function() {
    const mode = document.querySelector('#asm-mode input:checked').value
    const func = document.getElementById('asm-function').value
    const repl = document.getElementById('replace-check').checked

    if(!func) {
      editors.showText('; Please select a function to disassemble.')
      return
    }

    if(mode === 'target') {
      if(!target[func]) {
        editors.showText('; No such function in the target binary.')
      }
      else {
        let text = target[func].asm
        if(repl) text = editors.replace(text, 'target')
        editors.showText(TARGET_HEADER + text)
      }
    }
    else if(mode === 'candidate') {
      if(!candidate) {
        editors.showText('; Compile to get output.')
      }
      else if(!candidate['functions']) {
        editors.showText('; Compilation failed; see the console tab for details.')
      }
      else if(!candidate['functions'][func]) {
        editors.showText('; No such function in the candidate binary.')
      }
      else {
        let text = editors.candidate(func)
        let info = candidate.functions[func]
        if(repl) text = editors.replace(text, 'candidate')
        editors.showText(CANDIDATE_HEADER + text, info.srcmap)
      }
    }
    else {
      if(!candidate) {
        editors.showText('; Compile to get output.')
      }
      else if(!candidate['functions']) {
        editors.showText('; Compilation failed; see the console tab for details.')
      }
      else if(!candidate['functions'][func]) {
        editors.showText('; No such function.')
      }
      else {
        const info = candidate.functions[func]
        if(repl) {
          const tgt = editors.replace(editors.target(func), 'target')
          const cdt = editors.replace(editors.candidate(func), 'candidate')
          editors.showDiff(editors.diff(tgt, cdt), info.srcmap)
        }
        else {
          editors.showDiff(info.hunks, info.srcmap)
        }
      }
    }
  }
}
