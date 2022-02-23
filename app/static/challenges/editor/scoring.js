const scoring = {
  color: function(score) {
    const r = 2 * Math.min(0.5, 1 - score)
    const g = 2 * Math.min(0.5, score)
    return 'rgb(' + 128 * r + ', ' + 96 * g + ', 0)'
  },

  show: function(scores) {
    if(scores) {
      document.getElementById('score-ins').textContent = '-' + scores['ins']
      document.getElementById('score-del').textContent = '+' + scores['del']

      const pct = document.getElementById('score-pct')
      pct.textContent = Math.floor(100 * scores['total']) + '%'
      pct.style.color = scoring.color(scores['total'])
    }
    else {
      document.getElementById('score-ins').textContent = '-?'
      document.getElementById('score-del').textContent = '+?'
      document.getElementById('score-pct').textContent = '?%'

      const pct = document.getElementById('score-pct')
      pct.style.color = scoring.color(0)
      pct.textContent = '0%'
    }

    setcel = function(row, col, value, color) {
      const tb = document.getElementById('score-table')
      const tr = tb.children[row]
      const td = tr.children[col]

      td.textContent = Math.floor(100 * value) + '%'
      td.style.color = color
    }

    if(scores) {
      let score = scores['tests']
      let color = scoring.color(score)
      setcel(0, 4, score * 0.2, color)
      setcel(0, 2, score, color)

      score = scores['diffs']
      color = scoring.color(score)
      setcel(1, 4, score * 0.6, color)
      setcel(1, 2, score, color)

      score = scores['bonus']
      color = scoring.color(score)
      setcel(2, 3, score * 0.2, color)
      setcel(2, 1, score, color)

      score = scores['total']
      color = scoring.color(score)
      setcel(3, 3, score, color)
    }
    else {
      let color = scoring.color(0)
      setcel(0, 4, 0, color)
      setcel(0, 2, 0, color)
      setcel(1, 4, 0, color)
      setcel(1, 2, 0, color)
      setcel(2, 3, 0, color)
      setcel(2, 1, 0, color)
      setcel(3, 3, 0, color)
    }
  }
}
