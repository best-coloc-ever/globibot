<nav-bar>

  <header class="demo-drawer-header">
    <img src={ avatarUrl } class="demo-avatar">
    <div class="demo-avatar-dropdown">
      <span>{ username }</span>
      <div class="mdl-layout-spacer"></div>
      <button id="accbtn" class="mdl-button mdl-js-button mdl-js-ripple-effect mdl-button--icon">
        <i class="material-icons" role="presentation">arrow_drop_down</i>
        <span class="visuallyhidden">Accounts</span>
      </button>
      <ul class="mdl-menu mdl-menu--bottom-right mdl-js-menu mdl-js-ripple-effect" for="accbtn">
        <li class="mdl-menu__item hv-center" onclick={ logout }>
          <i class="material-icons">power_settings_new</i>
          <div class="mdl-layout-spacer"></div>
          Logout
        </li>
      </ul>
    </div>
  </header>

  <nav class="demo-navigation mdl-navigation mdl-color--blue-grey-800">

    <a class="mdl-navigation__link" href="#home">
      <i class="mdl-color-text--blue-grey-400 material-icons" role="presentation">home</i>Home
    </a>

    <a class="mdl-navigation__link" href="#logs">
      <i class="mdl-color-text--blue-grey-400 material-icons" role="presentation">book</i>
      Logs
      <span
        class={ 'mdl-badge': true, off: !logsWSConnected }
        data-badge=""
        id="logs-ws-badge">
      </span>
      <div class="mdl-tooltip mdl-tooltip--large" for="logs-ws-badge">
        Live notification: { logsWSConnected ? 'ON' : 'OFF' }
      </div>
    </a>

  </nav>

  <style scoped>
    #logs-ws-badge {
      margin-left: 30px;
    }
    #logs-ws-badge::after {
      margin-top: 3px;
      width: 15px;
      height: 15px;
      background: rgb(12, 232, 136);
    }
    #logs-ws-badge.off::after {
      background: rgb(232, 44, 12);
    }
  </style>

  <script>
    this.username = 'Nobody'
    this.avatarUrl = '//fakeimg.pl/300/?text=?'

    this.app = opts.app
    this.logsWSConnected = false

    this.logout = () => { riot.route('/logout') }

    this.app.on('credential-changed', () => {
      if (this.app.user) {
        this.username = this.app.user.name
        this.avatarUrl = this.app.user.avatar_url
      }
      else {
        this.username = 'Nobody'
        this.avatarUrl = '//fakeimg.pl/300/?text=?'
      }
      this.update()
    })

    this.app.on('on-logs-ws-open', () => {
      this.logsWSConnected = true
      this.update()
    })

    this.app.on('on-logs-ws-closed', () => {
      this.logsWSConnected = false
      this.update()
    })
  </script>

</nav-bar>
