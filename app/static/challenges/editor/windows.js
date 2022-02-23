const windows = {
  current: null,

  close: function() {
    document.getElementById('screen').style.display = 'none'
    if(windows.current !== null) {
      windows.current.classList.remove('active')
      windows.current = null
    }
  },

  escape: function() {
    let spinner = document.getElementById('spinner-win')
    if(windows.current !== spinner) {
      windows.close()
    }
  },

  open: function(id, screen) {
    if(windows.current !== null) {
      windows.current.classList.remove('active')
    }

    if(screen !== false) {
      document.getElementById('screen').style.display = 'block'
    }

    windows.current = document.getElementById(id)
    windows.current.classList.add('active')
  }
}
