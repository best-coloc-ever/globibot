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
          <!-- <div class="mdl-card__actions mdl-card--border"> -->
            <!-- <a class="mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect"
               if={ !connected }
               onclick={ connectTwitter }>
              Connect to Twitter
            </a>
            <a class="mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect"
               if={ connected }
               onclick={ disconnectTwitter }>
              Disconnect from Twitter
            </a> -->
          <!-- </div> -->
        </div>
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
  </style>


  <!-- logic -->
  <script>
    import API from '../api.js'

    this.twitterConnected = false

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

    this.on('mount', () => {
      API.twitterStatus()
        .then(data => {
          console.log(data)
          this.twitterConnected = data.connected
          this.update()
          componentHandler.upgradeElements(this.root)
        })
    })
  </script>

</connections-view>
