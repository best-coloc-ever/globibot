<connections-view>

  <!-- layout -->
  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">

    <h4 align="center">Connections</h4>

    <div class="mdl-grid">

      <div class="mdl-cell mdl-cell--4-col"></div>

      <div class="mdl-cell mdl-cell--4-col">
        <div class="mdl-card mdl-shadow--2dp">

          <div class="mdl-card__title" id="logs-title">
            <div class="mdl-cell mdl-cell--2-col">
              <img src="/dist/img/twitter.png"></img>
            </div>
            <div class="mdl-cell mdl-cell--7-col">
              <h2 class="mdl-card__title-text">Twitter</h2>
            </div>
            <div class="mdl-cell mdl-cell--2-col">
              <label class="mdl-switch mdl-js-switch">
                <input
                  type="checkbox"
                  class="mdl-switch__input"
                  onchange={ onTwitterSwitch }
                  checked={ twitterConnected }>
              </label>
            </div>
          </div>

          <div class="mdl-card__supporting-text">
            Allows you to use the <span class="command">!like</span> and
            <span class="command">!rt</span> commands
            when Globibot post tweets in a channel
          </div>
        </div>
      </div>

    </div>

    <hr>

    <div class="mdl-grid">

      <div class="mdl-cell mdl-cell--4-col"></div>

      <div class="mdl-cell mdl-cell--4-col">
        <div class="mdl-card mdl-shadow--2dp">

          <div class="mdl-card__title" id="logs-title">
            <div class="mdl-cell mdl-cell--2-col">
              <img src="/dist/img/twitch.png"></img>
            </div>
            <div class="mdl-cell mdl-cell--7-col">
              <h2 class="mdl-card__title-text">Twitch</h2>
            </div>
            <div class="mdl-cell mdl-cell--2-col">
              <label class="mdl-switch mdl-js-switch">
                <input
                  type="checkbox"
                  class="mdl-switch__input"
                  onchange={ onTwitchSwitch }
                  checked={ twitchConnected }>
              </label>
            </div>
          </div>

          <div class="mdl-card__supporting-text">
            Allows you to get notified on Discord when streamers you like go live
          </div>
        </div>
      </div>

    </div>

    <div class="mdl-grid" name="spinner" if={ twitchConnected && !twitchMonitoredChannels }>
      <div class="mdl-cell mdl-cell--3-col"></div>
      <div class="mdl-cell mdl-cell--6-col">
        <div class="mdl-progress mdl-js-progress mdl-progress__indeterminate">
        </div>
      </div>
    </div>

    <div class="mdl-grid" if={ twitchMonitoredChannels }>
      <div class="mdl-cell mdl-cell--4-col"></div>

      <div class="mdl-cell mdl-cell--4-col">
        <table class="mdl-data-table mdl-js-data-table" name="twitch-table-monitored">
          <tr>
            <th class="mdl-data-table__cell--non-numeric" style="width:100%">Channel</th>
            <th class="mdl-data-table__cell--non-numeric">
              <span id="twitch-mentions">Mention</span>
              <div class="mdl-tooltip" data-mdl-for="twitch-mentions">
                Get tagged whenever a server<br>monitored channel goes live
              </div>
            </th>
          </tr>

          <tr each={ channel in twitchMonitoredChannels }>
            <td class="mdl-data-table__cell--non-numeric">{ channel.name }</td>
            <td>
              <label class="mdl-switch mdl-js-switch">
                <input
                  type="checkbox"
                  class="mdl-switch__input"
                  onchange={ channelMention(channel.name) }
                  checked={ channel.on }>
              </label>
            </td>
          </tr>
        </table>
      </div>
    </div>

    <div class="mdl-grid" if={ twitchFollowedChannels }>
      <div class="mdl-cell mdl-cell--4-col" each={ channels in twitchFollowedChannels }>

        <table class="mdl-data-table mdl-js-data-table" name="twitch-table-followed">
          <tr>
            <th class="mdl-data-table__cell--non-numeric" style="width:100%">Channel</th>
            <th class="mdl-data-table__cell--non-numeric">
              <span id="twitch-whispers">Whisper</span>
              <div class="mdl-tooltip" data-mdl-for="twitch-whispers">
                Get whispered whenever a channel<br>you follow goes live
              </div>
            </th>
          </tr>

          <tr each={ channel in channels }>
            <td class="mdl-data-table__cell--non-numeric">{ channel.name }</td>
            <td>
              <label class="mdl-switch mdl-js-switch">
                <input
                  type="checkbox"
                  class="mdl-switch__input"
                  onchange={ channelWhisper(channel.name) }
                  checked={ channel.on }>
              </label>
            </td>
          </tr>
        </table>
      </div>
    </div>

  </div>


  <!-- style -->
  <style scoped>
    img {
      width: 28px;
      height: 28px;
    }

    .command {
      background-color: #37474F;
      color: white;
      border-radius: 3px;
      padding: .2em;
      font-size: 85%;
    }

    .mdl-card {
      min-height: 50px;
    }

    table {
      width: 100%;
    }
  </style>


  <!-- logic -->
  <script>
    import API from '../api.js'

    this.twitterConnected = false
    this.twitchConnected = false
    this.twitchMonitoredChannels = null
    this.twitchFollowedChannels = null

    this.onTwitterSwitch = (event) => {
      if (event.target.checked)
        this.connectTwitter()
      else
        this.disconnectTwitter()
    }

    this.connectTwitter = () => {
      API.twitterOAuthToken()
        .then(data => {
          window.location.href = `https://api.twitter.com/oauth/authorize?oauth_token=${data.token}`
        })
    }

    this.disconnectTwitter = () => {
      API.twitterDisconnect()
        .then(data => {
          this.update()
        })
    }

    this.onTwitchSwitch = () => {
      if (event.target.checked)
        this.connectTwitch()
      else
        this.disconnectTwitch()
    }

    this.connectTwitch = () => {
      window.location.href = API.twitchOAuthUrl()
    }

    this.disconnectTwitch = () => {
      API.twitchDisconnect()
        .then(data => {
          this.update()
        })
    }

    this.channelMention = name => () => {
      API.twitchMention(name, event.target.checked)
        .then(data => {

        })
    }
    this.channelWhisper = name => () => {
      API.twitchWhisper(name, event.target.checked)
        .then(data => {

        })
    }

    this.on('mount', () => {
      API.twitterStatus()
        .then(data => {
          this.twitterConnected = data.connected
          return API.twitchStatus()
        })
        .then(data => {
          this.twitchConnected = data.connected
          this.update()
          componentHandler.upgradeElements(this.root)
          if (this.twitchConnected) {
            API.twitchFollowed()
              .then(data => {
                this.twitchMonitoredChannels = data.monitored
                let chunkSize = Math.round(data.followed.length / 3)
                this.twitchFollowedChannels = [
                  data.followed.slice(0, chunkSize),
                  data.followed.slice(chunkSize, chunkSize * 2),
                  data.followed.slice(chunkSize * 2)
                ]
                this.update()
                componentHandler.upgradeElements(this['twitch-table-monitored'])
                componentHandler.upgradeElements(this['twitch-table-followed'])
                componentHandler.upgradeElements(this['spinner'])
              })
          }
        })
    })
  </script>

</connections-view>
