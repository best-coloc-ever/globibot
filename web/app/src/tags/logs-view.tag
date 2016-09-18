<logs-view>

  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">
    <h4 align="center">Logs</h4>

    <div class="mdl-tabs mdl-js-tabs mdl-js-ripple-effect">
      <div class="mdl-grid" name="spinner" if={ !data }>
        <div class="mdl-cell mdl-cell--3-col"></div>
        <div class="mdl-cell mdl-cell--6-col">
          <div class="mdl-progress mdl-js-progress mdl-progress__indeterminate">
          </div>
        </div>
      </div>

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
          <div class="mdl-cell mdl-cell--1-col">
            <div>
              <label class="mdl-radio mdl-js-radio mdl-js-ripple-effect"
                     for={ `logs-opt-activity-${i}` }>
                <input type="radio"
                       id={ `logs-opt-activity-${i}` }
                       name={ `logs-opt-${i}` }
                       class="mdl-radio__button"
                       onclick={ updateDataShown(i, 'activity') }
                       checked>
                <span class="mdl-radio__label">Activity</span>
              </label>
            </div>
            <div>
              <label class="mdl-radio mdl-js-radio mdl-js-ripple-effect"
                     for={ `logs-opt-users-${i}` }>
                <input type="radio"
                       id={ `logs-opt-users-${i}` }
                       name={ `logs-opt-${i}` }
                       class="mdl-radio__button"
                       onclick={ updateDataShown(i, 'users') }>
                <span class="mdl-radio__label">Users</span>
              </label>
            </div>
          </div>
          <div class="mdl-cell mdl-cell--1-col"></div>
          <div class="mdl-cell mdl-cell--8-col">
            <div show={ dataShown(i) == 'activity' }>
              <day-activity-bar-chart
                data={ serverData.activity_per_day }
                title="Server activity per day">
              </day-activity-bar-chart>
              <channel-activity-bar-chart
                data={ serverData.activity_per_channel }
                title="Server activity per channel in the last 24 hours">
              </channel-activity-bar-chart>
            </div>
            <table class="mdl-data-table mdl-js-data-table"
                   show={ dataShown(i) == 'users' }
                   name="userTable">
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
                  <a href={ '#logs/' + item.user.id }>
                    { item.user.name || '#' + item.user.id }
                  </a>
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
    this._dataShown = new Map

    this.updateDataShown = (index, dataType) => {
      return () => {
        this._dataShown.set(index, dataType)
        this.update()
      }
    }

    this.dataShown = (index) => {
      if (!this._dataShown.has(index))
        return 'activity'
      else
        return this._dataShown.get(index)
    }

    this.on('mount', () => {
      componentHandler.upgradeElements(this['spinner'])

      API.logs().then(data => {
        this.data = data
        this.update()
        componentHandler.upgradeElements(this.root)
      })

      opts.app.on('on-logs-ws-message', data => {
        for (let i = 0; i < this.data.length; ++i) {
          if (this.data[i].server_id == data.server.id) {

            // Day activity
            this.data[i].activity_per_day[0].action += 1
            if (data.message.type == 'original')
              this.data[i].activity_per_day[0].unique += 1
            else if (data.message.type == 'deleted')
              this.data[i].activity_per_day[0].deleted += 1

            // Channel activity
            for (let j = 0; j < this.data[i].activity_per_channel.length; ++j) {
              if (this.data[i].activity_per_channel[j].channel.id == data.channel.id) {
                this.data[i].activity_per_channel[j].action += 1
                if (data.message.type == 'original')
                  this.data[i].activity_per_channel[j].unique += 1
                else if (data.message.type == 'deleted')
                  this.data[i].activity_per_channel[j].deleted += 1
                break
              }
            }

            // user data
            if (data.message.type == 'original') {
              for (let j = 0; j < this.data[i].data.length; ++j) {
                if (this.data[i].data[j].user.id == data.author.id) {
                  console.log('user updated')
                  this.data[i].data[j].count += 1
                  break
                }
              }
            }

            break
          }
        }
        this.update()
      })
    })
  </script>

</logs-view>
