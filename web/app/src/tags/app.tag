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
    import API from '../api.js'
    import Cookies from 'js-cookie'

    this.user = null
    this.currentView = null
    this.logsWS = null

    this.setView = (viewTag, loginRequired=true, opts={}) => {
      if (loginRequired && !Cookies.get('user'))
        return riot.route('/login')

      if (this.currentView)
        this.currentView.unmount(true)

      opts.app = this
      this.currentView = riot.mount('view', viewTag, opts)[0]
    }

    this.on('mount', () => {
      riot.route('/',         ()        => { this.setView('home-view')            })
      riot.route('/login',    ()        => { this.setView('login-view', false)    })
      riot.route('/logout',   ()        => { this.logout() })
      riot.route('/register', ()        => { this.setView('register-view', false) })
      riot.route('/home',     ()        => { this.setView('home-view')            })
      riot.route('/logs',     ()        => { this.setView('logs-view')            })
      riot.route('/logs/*',   (userId)  => { this.setView('logs-view-user', true, { userId: userId }) })
      riot.route('/giveaways',()        => { this.setView('giveaways') })
      riot.route('/dj-admin', ()        => { this.setView('dj-admin-view') })
      riot.route('/dj',       ()        => { this.setView('dj-view') })
      riot.route('/connections', ()        => { this.setView('connections-view') })
      riot.route('/game-stats', ()        => { this.setView('game-stats-view') })
      riot.route('/game-stats/game/*', (game)        => {
        this.setView('game-stats-game-view', true, { game: game })
      })
      riot.route('/game-stats/user/*', (userId)        => {
        this.setView('game-stats-user-view', true, { userId: userId })
      })

      riot.route.start(true)

      if (!this.user) {
        if (Cookies.get('user')) {
          this.fetchUserData()

          let ws = API.logsWebSocket()
          ws.onopen    = e => { this.trigger('on-logs-ws-open')            }
          ws.onmessage = e => { this.trigger('on-logs-ws-message', JSON.parse(e.data)) }
          ws.onclose   = e => { this.trigger('on-logs-ws-closed')          }
          ws.onerror   = e => { this.trigger('on-logs-ws-error')           }
          setInterval(() => { ws.send('PING') }, 50 * 1000)
          this.logsWS = ws
        }
        else
          riot.route('/login')
      }
    })

    this.logout = () => {
      Cookies.remove('user')
      this.user = null
      this.trigger('credential-changed')
      riot.route('/login')
    }

    this.fetchUserData = () => {
      API.currentUser().then(data => {
        this.user = data
        this.trigger('credential-changed')
      })
    }

  </script>

</app>
