const sharing = {
  open: function(event) {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
      let DONE = this.DONE || 4
      if(this.readyState !== DONE) {
        return
      }

      if(this.status !== 200) {
        windows.open('error-win')
        return
      }

      let json = JSON.parse(this.responseText)
      let tbl  = document.getElementById('sharing-tbl')
      while(tbl.firstChild) {
        tbl.removeChild(tbl.firstChild);
      }

      // Poor man's HTML escaper:
      // https://stackoverflow.com/a/25396011
      let span = document.createElement('span')

      for(const item of json) {
        span.textContent = item.author

        tbl.insertAdjacentHTML('beforeend', `<tr>
          <td>
            <label>
              <input name="id" type="radio" value="${item.id}" />
              ${span.innerHTML}
            </label>
          </td>
          <td style="color:${scoring.color(item.score)}">${Math.floor(100 * item.score)}%</td>
        </tr>`)
      }

      windows.open('sharing-win')
    }

    windows.open('spinner-win')
    xhr.open('GET', window.location.pathname + '/submissions.json')
    xhr.send()

    if(event) {
      event.stopPropagation()
      event.preventDefault()
    }
  },

  doit: function(event) {
    if(event) {
      event.stopPropagation()
      event.preventDefault()
    }

    let tbl = document.getElementById('sharing-tbl')
    let inp = tbl.querySelector('input:checked')
    if(!inp) return

    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function() {
      let DONE = this.DONE || 4
      if(this.readyState !== DONE) {
        return
      }

      if(this.status !== 200) {
        windows.open('error-win')
        return
      }

      let json = JSON.parse(this.responseText)
      editors.code(json.source)
      editors.modified = false
      parent = json.id // global
      windows.close()
    }

    windows.open('spinner-win')
    xhr.open('GET', window.location.pathname + '/submissions/' + inp.value + '.json')
    xhr.send()
  }
}
