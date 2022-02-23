const notices = {
  common_regex: /^[^:]*:(\d+):(\d+): (\w+): (.*)$/mg,
  go_regex:     /^[^:]*:(\d+):(\d+): (.*)$/mg,
  nim_regex:    /^[^(]*\((\d+), (\d+)\) (\w+): (.*)$/mg,
  rust_regex:   /^(\w+)(?:\[\w+\])?: (.*)\n --> [^:]*:(\d+):(\d+)$/mg,

  auto: function(text) {
    let callback = notices[language]
    if(callback) return callback(text)

    console.warn('No parser for language "' + language +'".')
    return []
  },

  common: function(text) {
    let codemarkers = []

    // Not actually replacing things - just an easy way to loop:
    text.replace(notices.common_regex, function(m, l, c, v, x) {
      if(v !== 'note') codemarkers.push({row: l - 1, column: c, text: x, type: v})
    })

    return codemarkers
  },

  c: function(text) {
    return notices.common(text)
  },

  cpp: function(text) {
    return notices.common(text)
  },

  go: function(text) {
    let codemarkers = []

    // Not actually replacing things - just an easy way to loop:
    text.replace(notices.go_regex, function(m, l, c, x) {
      codemarkers.push({row: l - 1, column: c, text: x, type: 'error'})
    })

    return codemarkers
  },

  nim: function(text) {
    let codemarkers = []

    // Not actually replacing things - just an easy way to loop:
    text.replace(notices.nim_regex, function(m, l, c, v, x) {
      codemarkers.push({row: l - 1, column: c, text: x, type: v.toLowerCase()})
    })

    return codemarkers
  },

  rust: function(text) {
    let codemarkers = []

    // Not actually replacing things - just an easy way to loop:
    text.replace(notices.rust_regex, function(m, v, x, l, c) {
      codemarkers.push({row: l - 1, column: c, text: x, type: v})
    })

    return codemarkers
  },

  swift: function(text) {
    return notices.common(text)
  }
}
