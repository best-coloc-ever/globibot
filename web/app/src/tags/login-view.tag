<login-view>

  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">

    <h5 align="center">Login</h5>

    <div style="text-align:center;" >

      <div class="md-grid">
        <div class="md-cell mdl-textfield mdl-js-textfield">
          <input class="mdl-textfield__input" type="text" id="username">
          <label class="mdl-textfield__label" for="username">Username...</label>
        </div>
      </div>

      <div class="md-grid">
        <div class="md-cell mdl-textfield mdl-js-textfield">
          <input class="mdl-textfield__input" type="password" id="password">
          <label class="mdl-textfield__label" for="password">Password...</label>
        </div>
      </div>

      <div class="md-grid">
        <button class="mdl-button mdl-js-button mdl-button--colored mdl-button--raised" onclick={ finishLogin }>
          Let's go
        </button>
      </div>

      <div class="md-grid" style="text-align: right">
        <h6>New to this ? <a href="#register">Register first</a></h6>
      </div>

      <div class="mdl-snackbar mdl-js-snackbar" id="token-snackbar">
        <div class="mdl-snackbar__text"></div>
        <button class="mdl-snackbar__action" show={ false }></button>
      </div>

    </div>

    </div>
  </div>

  <style scoped>
    h6 {
      margin-right: 20px;
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
            riot.route('/home')
          }
          else {
            let data = { message: 'Invalid credentials' }
            let snackbar = document.getElementById('token-snackbar')
            snackbar.MaterialSnackbar.showSnackbar(data)
          }
        })
    }
  </script>

</login-view>
