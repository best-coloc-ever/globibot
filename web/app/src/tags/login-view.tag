<login-view>

  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">

    <h5 align="center">Login</h5>

    <div>

      <form action="#" onsubmit={ finishLogin }>
        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--4-col"></div>
          <div class="mdl-cell mdl-cell--4-col mdl-textfield mdl-js-textfield">
            <input class="mdl-textfield__input" type="text" id="username">
            <label class="mdl-textfield__label" for="username">Username...</label>
          </div>
          <div class="mdl-cell mdl-cell--1-col info">
            <i class="material-icons" id="login-tt" tabindex="-1">info_outline</i>
            <div class="mdl-tooltip" data-mdl-for="login-tt">
              Your <span class="important">current</span> Discord username
            </div>
          </div>
          <div class="mdl-cell mdl-cell--3-col"></div>
        </div>

        <div class="mdl-grid">
          <div class="mdl-layout-spacer"></div>
          <div class="mdl-cell mdl-cell--4-col mdl-textfield mdl-js-textfield">
            <input class="mdl-textfield__input" type="password" id="password">
            <label class="mdl-textfield__label" for="password">Password...</label>
          </div>
          <div class="mdl-layout-spacer"></div>
        </div>

        <div class="mdl-grid">
          <div class="mdl-layout-spacer"></div>
          <button class="mdl-button mdl-js-button mdl-button--colored mdl-button--raised">
            Let's go
          </button>
          <div class="mdl-layout-spacer"></div>
        </div>
      </form>

      <div class="mdl-grid">
        <div class="mdl-layout-spacer"></div>
        <h6>New to this ? <a href="#register">Register first</a></h6>
        <div class="mdl-layout-spacer"></div>
      </div>

      <div class="mdl-snackbar mdl-js-snackbar" id="token-snackbar">
        <div class="mdl-snackbar__text"></div>
        <button class="mdl-snackbar__action" show={ false }></button>
      </div>

    </div>

    </div>
  </div>

  <style scoped>
    .important {
      font-size: larger;
      font-weight: bold;
      color: yellow;
    }

    .info {
      padding-top: 20px;
      color: rgba(0, 0, 0, .25);
      cursor: default;
    }

    button a {
      color: white;
      text-decoration: none;
    }
  </style>

  <script>
    var self = this;

    this.app = opts.app

    this.on('mount', () => { componentHandler.upgradeElements(this.root) })

    this.finishLogin = () => {
      let form = new FormData()
      form.append('user', document.getElementById('username').value)
      form.append('password', document.getElementById('password').value)

      let requestSettings = {
        method: 'POST',
        body: form,
        credentials: 'same-origin'
      }

      fetch('/bot/api/login', requestSettings)
        .then(response => {
          if (response.ok) {
            this.app.fetchUserData()
            riot.route('/home')
          }
          else {
            let data = { message: 'Invalid credentials' }
            let snackbar = document.getElementById('token-snackbar')
            snackbar.MaterialSnackbar.showSnackbar(data)
          }
        })

      return false
    }
  </script>

</login-view>
