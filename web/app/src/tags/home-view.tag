<home-view>

  <div class="mdl-grid">

    <div class="mdl-cell mdl-cell--3-col">
      <div class="mdl-card mdl-shadow--2dp">
        <div class="mdl-card__title" id="logs-title">
          <div class="mdl-cell mdl-cell--2-col">
            <i class="mdl-color-text--blue-grey-400 material-icons">book</i>
          </div>
          <div class="mdl-cell mdl-cell--9-col">
            <h2 class="mdl-card__title-text">Server logs</h2>
          </div>
        </div>
         <div class="mdl-card__supporting-text">
          Browse public logs on the servers you and Globibot have in common
        </div>
        <div class="mdl-card__actions mdl-card--border">
          <a class="mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect" href="#logs">
            View logs
          </a>
        </div>
      </div>
    </div>

    <div class="mdl-cell mdl-cell--1-col"></div>

    <div class="mdl-cell mdl-cell--3-col">
      <div class="mdl-card mdl-shadow--2dp">
        <div class="mdl-card__title" id="logs-title">
          <div class="mdl-cell mdl-cell--2-col">
            <i class="mdl-color-text--blue-grey-400 material-icons">card_giftcard</i>
          </div>
          <div class="mdl-cell mdl-cell--9-col">
            <h2 class="mdl-card__title-text">Giveaways</h2>
          </div>
        </div>
         <div class="mdl-card__supporting-text">
          Show everyone on your server how generous you truly are
        </div>
        <div class="mdl-card__actions mdl-card--border">
          <a class="mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect" href="#giveaways">
            Give stuff away
          </a>
        </div>
      </div>
    </div>

    <div class="mdl-cell mdl-cell--1-col"></div>

    <div class="mdl-cell mdl-cell--3-col">
      <div class="mdl-card mdl-shadow--2dp">
        <div class="mdl-card__title">
          <h2 class="mdl-card__title-text">Cool stuff comming soon ™</h2>
        </div>
         <div class="mdl-card__supporting-text">
          <img src="//cdn.discordapp.com/emojis/219941501671571467.png">
        </div>
      </div>
    </div>

  </div>

  <div class="mdl-grid" each={ [1,2,3] }>

    <div class="mdl-cell mdl-cell--3-col">
      <div class="mdl-card mdl-shadow--2dp">
        <div class="mdl-card__title">
          <h2 class="mdl-card__title-text">Cool stuff comming soon ™</h2>
        </div>
         <div class="mdl-card__supporting-text">
          <img src="//cdn.discordapp.com/emojis/219941501671571467.png">
        </div>
      </div>
    </div>

    <div class="mdl-cell mdl-cell--1-col"></div>

    <div class="mdl-cell mdl-cell--3-col">
      <div class="mdl-card mdl-shadow--2dp">
        <div class="mdl-card__title">
          <h2 class="mdl-card__title-text">Cool stuff comming soon ™</h2>
        </div>
         <div class="mdl-card__supporting-text">
          <img src="//cdn.discordapp.com/emojis/219941501671571467.png">
        </div>
      </div>
    </div>

    <div class="mdl-cell mdl-cell--1-col"></div>

    <div class="mdl-cell mdl-cell--3-col">
      <div class="mdl-card mdl-shadow--2dp">
        <div class="mdl-card__title">
          <h2 class="mdl-card__title-text">Cool stuff comming soon ™</h2>
        </div>
         <div class="mdl-card__supporting-text">
          <img src="//cdn.discordapp.com/emojis/219941501671571467.png">
        </div>
      </div>
    </div>

  </div>

  <style scoped>
    .mdl-card__title {
      height: 80px
    }
  </style>

  <script>
    this.on('mount', () => {
      componentHandler.upgradeElements(this.root)
    })
  </script>

</home-view>
