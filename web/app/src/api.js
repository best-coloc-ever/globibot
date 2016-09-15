const credentials = { credentials: 'same-origin' }

class API {

  static currentUser()       { return API.jsonCall('/api/user')                }
  static server(snowflake)   { return API.jsonCall('/api/server/' + snowflake) }
  static logs()              { return API.jsonCall('/logs/top')                }
  static userLogs(snowflake) { return API.jsonCall('/logs/user/' + snowflake)  }

  static jsonCall(route) {
    let promise =
      fetch(API.path(route), credentials)
        .then(response => {
          if (response.ok)
            return response.json()
          else
            throw new Error(response.status)
        })

    return promise
  }

  static path(suffix) {
    return '/bot' + suffix
  }

}

module.exports = API
