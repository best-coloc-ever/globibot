<register-view>

  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">

    <h5 align="center">Register</h5>

    <div>

      <div class="mdl-grid">
        <div class="mdl-cell mdl-cell--4-col"></div>
        <div class="mdl-cell mdl-cell--4-col mdl-textfield mdl-js-textfield">
          <input class="mdl-textfield__input" type="text" id="username" onkeyup={ searchUsername }>
          <label class="mdl-textfield__label" for="username">Your Discord username</label>
        </div>
        <div class="mdl-cell mdl-cell--1-col hv-center" show={ searchingUsername }>
          <div class="mdl-spinner mdl-js-spinner is-active"></div>
        </div>
        <div class="mdl-cell mdl-cell--1-col hv-center" show={ !searchingUsername }>
          <i class="material-icons" show={ usernameValidated }>done</i>
          <i class="material-icons" show={ usernameValidated == false }>clear</i>
        </div>
      </div>

      <div class="mdl-grid" show={ usernameValidated }>
        <div class="mdl-cell mdl-cell--col-4"></div>
        <div class="mdl-cell mdl-cell--col-4">
          <div class="mdl-grid hv-center">
            Hi { user.name }, is this you ?
          </div>
          <div class="mdl-grid hv-center">
            <img src={ user.avatar_url }>
          </div>
          <div class="mdl-grid hv-center">
            <button class="mdl-button mdl-js-button mdl-button--colored mdl-button--raised" onclick={ sendToken }>
              Yes that's me 👍
            </button>
            <div class="mdl-snackbar mdl-js-snackbar" id="token-snackbar">
              <div class="mdl-snackbar__text"></div>
              <button class="mdl-snackbar__action" show={ false }></button>
            </div>
          </div>
        </div>
      </div>

      <div show={ tokenSent }>
        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--4-col"></div>
          <div class="mdl-cell mdl-cell--4-col mdl-textfield mdl-js-textfield">
            <input class="mdl-textfield__input" type="text" id="token">
            <label class="mdl-textfield__label" for="token">Paste your token here...</label>
          </div>
        </div>
        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--4-col"></div>
          <div class="mdl-cell mdl-cell--4-col mdl-textfield mdl-js-textfield">
            <input class="mdl-textfield__input" type="password" id="password">
            <label class="mdl-textfield__label" for="password">Choose a password...</label>
          </div>
        </div>
        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--4-col"></div>
          <div class="mdl-cell mdl-cell--4-col hv-center">
            <button class="mdl-button mdl-js-button mdl-button--colored mdl-button--raised" onclick={ finishRegistration }>
              <a href="#">Let's go</a>
            </button>
          </div>
        </div>
      </div>

      <div class="mdl-grid" show={ identityValidated }>

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
    button {
      margin-bottom: 24px;
    }
    .hv-center {
      display: flex;
      justify-content: center;
      align-items: center;
    }
  </style>

  <script>
    var self = this

    this.usernameValidated = null
    this.searchingUsername = false
    this.tokenSent = false
    this.user = null

    this.on('mount', () => { componentHandler.upgradeElements(this.root) })

    var searchDebouncer = null
    this.searchUsername = (event) => {
      if (searchDebouncer)
        clearInterval(searchDebouncer)

      let username = event.target.value
      searchDebouncer = setTimeout(() => {
        self.searchingUsername = true
        self.usernameValidated = false
        self.update()

        fetch('/bot/api/find?user_name=' + username)
          .then(response => {
            self.searchingUsername = false

            if (!response.ok)
              this.usernameValidated = false
            else {
              this.usernameValidated = true
              response.json().then(j => {
                self.user = j
                self.update()
              })
            }
            self.update()
          })
      }, 500)
    }

    this.sendToken = (event) => {
      fetch('/bot/api/send-registration-token/' + self.user.id, { method: 'POST' })
        .then(response => {
          self.tokenSent = true

          let message = response.ok ? 'I whispered you a code on Discord :)'
                                    : 'I already whispered you a code on Discord'

          let snackbar = document.getElementById('token-snackbar')
          let data = { message: message }
          snackbar.MaterialSnackbar.showSnackbar(data)

          self.update()
        })
    }

    this.finishRegistration = (event) => {
      let form = new FormData()
      form.append('user', self.user.id)
      form.append('token', document.getElementById('token').value)
      form.append('password', document.getElementById('password').value)

      let requestSettings = {
        method: 'POST',
        body: form
      }

      fetch('/bot/api/register', requestSettings)
        .then(response => {
          if (!response.ok) {
            response.text().then(text => {
              let data = { message: text }
              let snackbar = document.getElementById('token-snackbar')
              snackbar.MaterialSnackbar.showSnackbar(data)
            })
          }
          else
            riot.route('/login')
        })
    }
  </script>


</register-view>
