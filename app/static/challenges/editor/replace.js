const find = {
  editor: null,

  next: function(event) {
    let src = document.getElementById('find-src').value
    editors.map['diff-view'].findNext({
      needle: src,
      wrap:   true
    })

    if(event) {
      event.stopPropagation()
      event.preventDefault()
    }
  },

  open: function() {
    let txt = editors.map['diff-view'].getSelectedText()
    let src = document.getElementById('find-src')

    windows.open('find-win', false)
    if(txt !== '') {
      src.value = txt
    }

    src.focus()
  },

  prev: function(event) {
    let src = document.getElementById('find-src').value
    editors.map['diff-view'].findPrevious({
      needle: src,
      wrap:   true
    })

    if(event) {
      event.stopPropagation()
      event.preventDefault()
    }
  }
}

const replace = {
  doit: function(event) {
    let src = document.getElementById('replace-src').value
    let dst = document.getElementById('replace-dst').value

    editors.map['code-edit'].replaceAll(dst, {
      needle: src
    })

    windows.close()

    if(event) {
      event.stopPropagation()
      event.preventDefault()
    }
  },

  open: function() {
    let txt = editors.map['code-edit'].getSelectedText()
    let src = document.getElementById('replace-src')
    let dst = document.getElementById('replace-dst')

    windows.open('replace-win')
    if(txt !== '') {
      src.value = txt
      dst.focus()
    }
    else {
      src.focus()
    }
  }
}
