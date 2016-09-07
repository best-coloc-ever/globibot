 var webpack = require('webpack')

module.exports = {
  entry: {
    app: './src/index.js',
    vendor: './src/vendor.js'
  },

  output: {
    path: './dist',
    filename: 'bundle.js'
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
  ]
};
