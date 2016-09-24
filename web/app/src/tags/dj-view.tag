<dj-view>

  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">

    <h4 align="center">Dj</h4>

    <div class="mdl-tabs mdl-js-tabs mdl-js-ripple-effect">

      <div class="mdl-tabs__tab-bar">
        <a each={ voice, i in data }
           href={ '#dj-server-panel-' + i }
           class={ 'mdl-tabs__tab': true, 'is-active': (i == 0) }>
          <server
            snowflake={ voice.server.id }
            name={ voice.server.name }
            iconUrl={ voice.server.icon_url }>
          </server>
        </a>
      </div>

      <div each={ voice, i in data }
           class={ 'mdl-tabs__panel': true, 'is-active': (i == 0) }
           id={ 'dj-server-panel-' + i }>

        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--3-col"></div>
          <div class="mdl-cell mdl-cell--6-col">

            <div class="mdl-grid">
              <div class="mdl-cell mdl-cell--6-col">
                <div class="mdl-textfield mdl-js-textfield">
                  <textarea
                    class="mdl-textfield__input"
                    type="text"
                    rows= "3"
                    id={ 'queue-' + i }
                    name={ 'queue-' + i }
                    onkeyup={ onQueueKeyUp(voice.server.id, i) }></textarea>
                  <label class="mdl-textfield__label" for={ 'queue-' + i }>Link or Youtube search...</label>
                </div>
              </div>
              <div class="mdl-cell mdl-cell--6-col">
                <div class="mdl-textfield mdl-js-textfield">
                  <textarea
                    class="mdl-textfield__input"
                    type="text"
                    rows= "3"
                    id={ 'tts-' + i }
                    name={ 'tts-' + i }
                    onkeyup={ onTTSKeyUp(voice.server.id, i) }></textarea>
                  <label class="mdl-textfield__label" for={ 'tts-' + i }>TTS...</label>
                </div>
              </div>
            </div>

            <h4 align="center">Current playlist</h4>

            <playlist snowflake={ voice.server.id }></playlist>

          </div>
        </div>

      </div>

    </div>

  </div>

  <script>
    import API from '../api.js'

    this.ws = null
    this.data = null

    this.on('mount', () => {
      API.voiceInfo().then(data => {
        this.data = data
        this.update()
        componentHandler.upgradeElements(this.root)
        this.initWebSocket()
      })
    })

    this.initWebSocket = () => {
      let ws = API.voiceWebSocket()

      ws.onopen = (e) => { console.log('voice connected') }
      ws.onmessage = (e) => {
        let data = JSON.parse(e.data);
        this.trigger(`on-voice-data-${data.server_id}`, data)
      }
      ws.onclose = (e) => { console.log('voice closed') }
      ws.onerror = (e) => { console.log('voice error') }

      setInterval(() => { ws.send('PING') }, 50 * 1000)

      this.ws = ws
    }

    this.onQueueKeyUp = (serverId, i) => {
      return (event) => {
        if (event.keyCode == 13) {
          let queue = this['queue-' + i]
          let song = queue.value
          queue.value = ''
          this.update()
          API.queueSong(serverId, song)
        }
      }
    }

    this.onTTSKeyUp = (serverId, i) => {
      return (event) => {
        if (event.keyCode == 13) {
          let tts = this['tts-' + i]
          let content = tts.value
          tts.value = ''
          this.update()
          API.tts(serverId, content)
        }
      }
    }
  </script>

</dj-view>
