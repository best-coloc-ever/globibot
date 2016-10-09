const credentials = { credentials: 'same-origin' }

class API {

  static currentUser()       { return API.jsonCall('/api/user')                }
  static server(snowflake)   { return API.jsonCall(`/api/server/${snowflake}`) }
  static logs()              { return API.jsonCall('/logs/top')                }
  static userLogs(snowflake) { return API.jsonCall(`/logs/user/${snowflake}`)  }
  static giveawayInfo()      { return API.jsonCall('/giveaways/user')          }
  static twitterOAuthToken() { return API.jsonCall('/twitter/oauth_token')     }
  static twitterStatus()     { return API.jsonCall('/twitter/status')          }
  static twitterDisconnect() {
    return API.jsonCall('/twitter/disconnect', { method: 'POST' })
  }

  static giveawayStart(serverId, title, content) {
    let form = new FormData

    form.append('server_id', serverId)
    form.append('title',     title)
    form.append('content',   content)

    return API.jsonCall('/giveaways/start', { body: form, method: 'POST' })
  }

  static voiceInfo() {
    return API.jsonCall('/voice')
  }

  static voiceAction(data) {
    let form = new FormData

    for (var key in data)
      form.append(key, data[key])

    return API.jsonCall('/voice', { body: form, method: 'POST' })
  }

  static joinVoice(serverId, channelId) {
    return API.voiceAction({
      action_type: 'join',
      channel_id: channelId,
      server_id: serverId
    })
  }

  static tts(serverId, content) {
    return API.voiceAction({
      action_type: 'tts',
      server_id: serverId,
      content: content
    })
  }

  static queueSong(serverId, song) {
    return API.voiceAction({
      action_type: 'queue',
      server_id: serverId,
      song: song
    })
  }

  static logsWebSocket() {
    return new WebSocket(`wss://${document.domain}:8443/ws/logs`)
  }

  static voiceWebSocket() {
    return new WebSocket(`wss://${document.domain}:8443/ws/voice`)
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
