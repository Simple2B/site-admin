//webpack.config.js
const path = require('path');
const {merge} = require('webpack-merge');

const defaultConfig = {
  resolve: {
    extensions: ['.ts', '.tsx', '.js'],
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        loader: 'ts-loader',
      },
    ],
  },
};

const baseConfig = {
  entry: {
    main: './src/main.ts',
  },
  output: {
    path: path.resolve(__dirname, './app/static'),
    filename: 'js/mainmin.js', // <--- Will be compiled to this single file
  },
};

const userConfig = {
  entry: {
    main: './src/main.ts',
  },
  output: {
    path: path.resolve(__dirname, './app/static'),
    filename: 'js/main.js', // <--- Will be compiled to this single file
  },
};

const configs = [baseConfig, userConfig].map(conf =>
  merge(defaultConfig, conf),
);

module.exports = configs;
