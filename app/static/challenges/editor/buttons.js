const buttons = {
  init: function() {
    function tab(tab_id, panel_id) {
      for(const child of document.getElementById('recto').children) {
        child.classList.toggle('active', child.id === panel_id)
      }

      for(const child of document.getElementById('tabs').children) {
        child.classList.toggle('active', child.id === tab_id)
      }

      const editor = editors.map[panel_id]
      if(editor) editor.resize()
    }

    // Tab switchers...
    document.getElementById( 'comp-tab').addEventListener('click', e => tab( 'comp-tab',  'comp-view'))
    document.getElementById( 'diff-tab').addEventListener('click', e => tab( 'diff-tab',  'diff-view'))
    document.getElementById('score-tab').addEventListener('click', e => tab('score-tab', 'score-view'))

    // Compilation...
    document.getElementById('do-compile').addEventListener('click', e => buttons.compile())

    // Find...
    document.getElementById(   'find-btn' ).addEventListener('click',  e => find.open(e))
    document.getElementById(   'find-win' ).addEventListener('submit', e => find.next(e))
    document.getElementById('do-find-prev').addEventListener('click',  e => find.prev(e))
    document.getElementById('do-find-next').addEventListener('click',  e => find.next(e))

    // Replace...
    document.getElementById('replace-btn').addEventListener('click',  e => replace.open(e))
    document.getElementById('replace-win').addEventListener('submit', e => replace.doit(e))
    document.getElementById( 'do-replace').addEventListener('click',  e => replace.doit(e))

    // Code sharing...
    document.getElementById('sharing-btn').addEventListener('click',  e => sharing.open(e))
    document.getElementById('sharing-win').addEventListener('submit', e => sharing.doit(e))
    document.getElementById( 'do-sharing').addEventListener('click',  e => sharing.doit(e))

    document.getElementById('asm-opts').addEventListener('change', e => {
      editors.update()
    })

    for(const button of document.getElementsByClassName('cancel-btn')) {
      button.addEventListener('click', e => windows.close())
    }

    window.addEventListener('keydown', e => {
      if(e.key === 'Escape') {
        windows.escape()
      }
      else {
        return
      }

      e.stopPropagation()
      e.preventDefault()
    })

    document.getElementById('replace-text').addEventListener('click', e => {
      if(e.target.id == 'replace-text') windows.open('replacement-win')
    })

    document.getElementById('replacement-add').addEventListener('click', e => {
      const newrow = document.getElementById('replacement-template').cloneNode(true)
      const table  = document.getElementById('replacements')
      newrow.removeAttribute('id')
      table.appendChild(newrow)
    })

    document.getElementById('replacements').addEventListener('click', e => {
      if(e.target.classList.contains('x')) {
        const row = e.target.parentNode
        row.parentNode.remove(row)
      }
    })

    document.getElementById('replacement-done').addEventListener('click', e => {
      editors.update()
    })
  },

  compile: function() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
      let DONE = this.DONE || 4
      if(this.readyState !== DONE) {
        return
      }

      if(this.status === 403) {
        windows.open('finished-win')
        return
      }

      if(this.status !== 200) {
        windows.open('error-win')
        return
      }

      let json = JSON.parse(this.responseText)
      candidate = json // global
      parent = json.id // global

      scoring.show(json['scores'])
      editors.comp(json['stdout'])

      if(json['functions']) {
        editors.functions(json['functions'])
        var tab = 'diff-tab'
      }
      else {
        // editors.functions(target)
        var tab = 'comp-tab'
      }

      document.getElementById(tab).click()
      windows.close()
    }

    let data = new FormData()
    data.append('parent', parent)
    data.append('source', codeedit.getValue())
    document.querySelectorAll('#options-list input').forEach(input => {
      data.append('options', input.value)
    })

    editors.modified = false
    windows.open('spinner-win')
    xhr.open('POST', window.location)
    xhr.send(data)
  }
}
