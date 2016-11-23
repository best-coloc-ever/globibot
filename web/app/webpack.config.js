var webpack = require('webpack')
var CopyWebpackPlugin = require('copy-webpack-plugin')

var path = require('path')

module.exports = {
  entry: {
    app: './src/index.js',
    vendor: './src/vendor.js'
  },

  output: {
    path: '/dist',
    filename: 'bundle.js'
  },

  resolve: {
    root: [ path.resolve('./src') ]
  },

  module: {
    preLoaders: [
      { test: /\.tag$/, include: /src/, loader: 'riotjs', query: { type: 'none' } },
    ],
    loaders: [
      { test: /\.css$/, include: /src/, loader: 'style!css' },
      { test: /\.js$|\.tag$/, include: /src/, loader: 'babel', query: { presets: 'es2015-riot' } },
    ],
  },

  babel: {
    presets: ['es2015'],
  },

  plugins: [
    new webpack.ProvidePlugin({ riot: 'riot' }),
    new webpack.optimize.CommonsChunkPlugin(
      /* chunkName= */'vendor',
      /* filename= */'vendor.bundle.js'
    ),
    new CopyWebpackPlugin([
      { from: 'img', to: 'img' },
      { from: 'index.html' },
      { from: 'styles.css' },
      { from: 'favicon.png' },
    ]),
    new webpack.DefinePlugin({
      APP_CLIENT_ID: JSON.stringify(process.env.APP_CLIENT_ID),
    })
  ]
};
