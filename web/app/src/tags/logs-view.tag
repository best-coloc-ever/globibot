<logs-view>

  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">
    <h4 align="center">Logs</h4>

    <div class="mdl-tabs mdl-js-tabs mdl-js-ripple-effect">
      <div class="mdl-tabs__tab-bar">
        <a each={ serverData, i in data }
           href={ '#logs-server-panel-' + i }
           class={ 'mdl-tabs__tab': true, 'is-active': (i == 0) }>
          <server snowflake={ serverData.server_id }></server>
        </a>
      </div>

      <div each={ serverData, i in data }
           class={ 'mdl-tabs__panel': true, 'is-active': (i == 0) }
           id={ 'logs-server-panel-' + i }>
        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--2-col"></div>
          <div class="mdl-cell mdl-cell--8-col">
            <table class="mdl-data-table mdl-js-data-table">
              <tr>
                <th>#</th>
                <th class="mdl-data-table__cell--non-numeric">User</th>
                <th class="mdl-data-table__header--sorted-descending">
                  <span id={ 'count-tooltip-' + i }>Message count</span>
                  <div class="mdl-tooltip" data-mdl-for={ 'count-tooltip-' + i }>
                    Does not include edited messages
                  </div>
                </th>
              </tr>

              <tr each={ item, i in serverData.data }>
                <td>{ i + 1 }</td>
                <td class="mdl-data-table__cell--non-numeric">
                  <a href={ '#logs/' + item.user.id }>{ item.user.name }</a>
                </td>
                <td>{ item.count }</td>
              </tr>
            </table>
          </div>
        </div>
      </div>
    </div>

  </div>

  <style scoped>
    table {
      width: 100%;
    }
  </style>

  <script>
    import API from '../api.js'

    this.data = null

    this.on('mount', () => {
      API.logs().then(data => {
        this.data = data
        this.update()
        componentHandler.upgradeElements(this.root)
      })
    })
  </script>

</logs-view>
