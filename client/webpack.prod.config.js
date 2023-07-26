const path = require("path");

module.exports = {
    mode: "production",
    entry: {
        landing: "./src/scripts/index.js",
        faceted_search: "./src/scripts/faceted_search.js",
    },
    output: {
        path: path.resolve(__dirname, "client", "dist"),
        filename: "[name].js",
    },
};
