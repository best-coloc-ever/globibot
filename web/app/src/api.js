const credentials = { credentials: 'same-origin' }

class API {

  static currentUser()       { return API.jsonCall('/api/user')                }
  static server(snowflake)   { return API.jsonCall(`/api/server/${snowflake}`) }
  static logs()              { return API.jsonCall('/logs/top')                }
  static userLogs(snowflake) { return API.jsonCall(`/logs/user/${snowflake}`)  }
  static giveawayInfo()      { return API.jsonCall('/giveaways/user')          }

  static giveawayStart(serverId, title, content) {
    let form = new FormData

    form.append('server_id', serverId)
    form.append('title',     title)
    form.append('content',   content)

    return API.jsonCall('/giveaways/start', { body: form, method: 'POST' })
  }

  static logsWebSocket() {
    return new WebSocket(`wss://${document.domain}/ws/logs`)
  }

  static jsonCall(route, extra={}) {
    let init = Object.assign(extra, credentials)

    let promise =
      fetch(API.path(route), init)
        .then(response => {
          if (response.ok)
            return response.json()
          else
            throw new Error(response.status)
        })

    return promise
  }

  static path(suffix) {
    return '/bot' + suffix
  }

}

module.exports = API
