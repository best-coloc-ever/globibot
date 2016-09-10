<app>

  <div class="demo-layout mdl-layout mdl-js-layout mdl-layout--fixed-drawer mdl-layout--fixed-header">

    <header class="demo-header mdl-layout__header mdl-color--grey-100 mdl-color-text--grey-600">
      <div class="mdl-layout__header-row">
        <img src="favicon.png">
        <span class="mdl-layout-title">Globibot</span>
        <div class="mdl-layout-spacer"></div>
      </div>
    </header>

    <nav-bar class="demo-drawer mdl-layout__drawer mdl-color--blue-grey-900 mdl-color-text--blue-grey-50" app={ this }>

    </nav-bar>

    <main class="mdl-layout__content mdl-color--grey-100">
      <view class="mdl-grid demo-content"></view>
    </main>

  </div>

  <script>
    import Cookies from 'js-cookie'

    var self = this;

    this.user = null
    this.token = null
    this.currentView = null

    this.setView = (viewTag, loginRequired = true, opts={}) => {
      if (loginRequired && !Cookies.get('user'))
        return riot.route('/login')

      if (this.currentView)
        this.currentView.unmount(true)

      opts.app = this
      this.currentView = riot.mount('view', viewTag, opts)[0]
    }

    this.on('mount', () => {
      riot.route('/login',    ()        => { this.setView('login-view', false)    })
      riot.route('/register', ()        => { this.setView('register-view', false) })
      riot.route('/home',     ()        => { this.setView('home-view')            })
      riot.route('/logs',     ()        => { this.setView('logs-view')            })
      riot.route('/logs/*',   (userId) => { this.setView('logs-view-user', true, { userId: userId }) })

      riot.route.start(true)

      if (!self.user) {
        if (Cookies.get('user'))
          fetch('/bot/api/user', { credentials: 'same-origin' })
            .then(r => r.json())
            .then(data => {
              self.user = data
              console.log(self.user)
              self.trigger('credential-changed')
            })
        else
          riot.route('/login')
      }
    })
  </script>

</app>
