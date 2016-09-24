<dj-admin-view>

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
          <div class="mdl-cell mdl-cell--4-col"></div>
          <div class="mdl-cell mdl-cell--4-col">
            <div class="mdl-textfield mdl-js-textfield">
              <textarea
                class="mdl-textfield__input"
                type="text"
                rows= "3"
                id={ 'tts-' + i }
                name={ 'tts-' + i }
                onkeyup={ onKeyUp(voice.server.id, i) }></textarea>
              <label class="mdl-textfield__label" for={ 'tts-' + i }>TTS...</label>
            </div>
          </div>
        </div>

        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--4-col"></div>
          <div class="mdl-cell mdl-cell--4-col">
            <ul class="mdl-list">
              <li each={ channel in voice.channels } class="mdl-list__item">
                <span class="mdl-list__item-primary-content">
                  { channel.name }
                </span>
                <span class="mdl-list__item-secondary-action">
                  <button
                    class="mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect"
                    onclick={ joinChannel(voice.server.id, channel.id) }>
                    Join
                  </button>
                </span>
              </li>
            </ul>
          </div>
        </div>

      </div>

    </div>

  </div>

  <style scoped>
    img {
      width: 28px;
      height: 28px;
    }
  </style>

  <script>
    import API from '../api.js'

    this.data = null

    this.on('mount', () => {
      API.voiceInfo().then(data => {
        this.data = data
        this.update()
        componentHandler.upgradeElements(this.root)
      })
    })

    this.joinChannel = (serverId, channelId) => {
      return () => {
        API.joinVoice(serverId, channelId)
      }
    }

    this.onKeyUp = (serverId, i) => {
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

</dj-admin-view>
