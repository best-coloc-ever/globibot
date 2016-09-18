<giveaways>

  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">

    <h4 align="center">Giveaways</h4>

    <div class="mdl-grid" if={ data }>
      <div class="mdl-cell mdl-cell--2-col"></div>
      <div class="mdl-cell mdl-cell--8-col">

        <div class="mdl-grid hv-center">
          Pick the server for your Giveaway (you have { data.giveaway_count } giveaways left)
        </div>

        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--3-col"></div>
          <div class="mdl-cell mdl-cell--6-col">
            <ul class="mdl-list">
              <li class="mdl-list__item" each={ server in data.servers }>
                <span class="mdl-list__item-primary-content">
                  <img src={ server.icon_url }></img>
                  { server.name }
                </span>
                <span class="mdl-list__item-secondary-action">
                  <label class="mdl-radio mdl-js-radio mdl-js-ripple-effect" for={ `giveaway-server-list-${server.id}` }>
                    <input
                      type="radio"
                      id={ `giveaway-server-list-${server.id}` }
                      class="mdl-radio__button"
                      name="giveaway-server-opt"
                      onclick={ setServer(server.id) }>
                  </label>
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--3-col"></div>
          <div class="mdl-cell mdl-cell--6-col">
            <div class="mdl-textfield mdl-js-textfield">
              <input
                class="mdl-textfield__input"
                type="text"
                id="giveaway-title"
                name="giveaway-title"
                onkeyup={ updateGiveawayPossibility }>
              <label class="mdl-textfield__label" for="giveaway-title">Giveaway description...</label>
            </div>
          </div>
        </div>

        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--3-col"></div>
          <div class="mdl-cell mdl-cell--6-col">
            <div class="mdl-textfield mdl-js-textfield">
              <textarea
                class="mdl-textfield__input"
                type="text"
                rows= "3"
                id="giveaway-content"
                name="giveaway-content"
                onkeyup={ updateGiveawayPossibility }></textarea>
              <label class="mdl-textfield__label" for="giveaway-content">Giveaway content...</label>
            </div>
          </div>
        </div>

        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--3-col"></div>
          <div class="mdl-cell mdl-cell--6-col hv-center">
            <button
              class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored"
              disabled={ !canStartGiveaway }
              onclick={ startGiveaway }>
              Launch giveaway!
            </button>
          </div>
        </div>

        <div class="mdl-snackbar mdl-js-snackbar" name="snackbar">
          <div class="mdl-snackbar__text"></div>
          <button class="mdl-snackbar__action" show={ false }></button>
        </div>

      </div>
    </div>

  </div>

  <style scoped>
    img {
      height: 32px;
      width: 32px;
      margin-right: 10px;
    }

    label {
      display: inline;
    }
  </style>

  <script>
    import API from '../api.js'

    this.data = null
    this.canStartGiveaway = false
    this.serverId = null

    this.on('mount', () => {
      API.giveawayInfo().then(data => {
        this.data = data
        this.update()
        componentHandler.upgradeElements(this.root)
      })
    })

    this.updateGiveawayPossibility = () => {
      this.canStartGiveaway = (
        this.serverId &&
        this.data.giveaway_count > 0 &&
        this['giveaway-title'].value &&
        this['giveaway-content'].value
      )
      this.update()
    }

    this.setServer = serverId => {
      return () => {
        this.serverId = serverId
        this.updateGiveawayPossibility()
      }
    }

    this.startGiveaway = () => {
      API.giveawayStart(
        this.serverId,
        this['giveaway-title'].value,
        this['giveaway-content'].value
      ).then(data => {
        let snackbar = this['snackbar']
        snackbar.MaterialSnackbar.showSnackbar({ message: data.message })
      })
    }
  </script>

</giveaways>
