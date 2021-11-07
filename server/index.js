// express
const express = require("express");
const PORT = process.env.PORT || 3001;
const app = express();
require("dotenv").config();

// CORS
const cors = require("cors");
app.use(
  cors({
    origin: ["http://localhost:3000", "https://phillytrails.onrender.com/"],
  })
);

// postgres
const pg = require("pg");

let client;
if (process.env.NODE_ENV == "production") {
  client = new pg.Client({
    connectionString: process.env.DATABASE_URL,
    ssl: {
      rejectUnauthorized: false,
    },
  });
} else {
  client = new pg.Client({
    connectionString: process.env.DATABASE_URL,
  });
}
client.connect();

app.get("/", (req, res) => {
  res.send({ health: "OK" });
});

// TODO: error handling for bad table names
app.get("/api/v3/geojson/:table", (req, res) => {
  const table = req.params.table;
  client
    .query("SELECT ST_AsGeoJSON(" + table + ".*, 'geom') FROM " + table + ";")
    .then((result) => {
      res.send({
        type: "FeatureCollection",
        features: result.rows.map((r) => JSON.parse(r.st_asgeojson)),
      });
    });
});

app.get("/api/geojson/:table", (req, res) => {
  const table = req.params.table;

  client
    .query("SELECT * FROM " + table + " WHERE false;")
    .then((result) => {
      const props = result.fields
        .map((p) => p.name)
        .filter((p) => p != "id_0")
        .filter((p) => p != "OBJECTID")
        .filter((p) => p != "geom");
      let proplist = "";
      for (let i = 0; i < props.length; i++) {
        proplist += "'" + props[i] + "', " + props[i] + ", ";
      }
      return proplist;
    })
    .then((proplist) => {
      const queryString =
        `SELECT json_build_object(
        'type',       'Feature',
        'geometry',   ST_AsGeoJSON(geom)::json,
        'properties', json_build_object(` +
        proplist.substring(0, proplist.length - 2) +
        `
         )
     )
     FROM ` +
        table +
        `;`;
      client.query(queryString).then((result) => {
        res.send({
          type: "FeatureCollection",
          features: result.rows.map((r) => r.json_build_object),
        });
      });
    });
});

app.get("/api/center/trail/:id", (req, res) => {
  client
    .query(
      `SELECT ST_AsText(pt) AS centroid, ST_AsText(ST_ClosestPoint(line,pt)) AS line_point
    FROM (
      SELECT ST_Centroid(geom) AS pt, geom AS line
      FROM trails
      WHERE id = ` +
        req.params.id +
        `
    ) AS feature`
    )
    .then((result) => {
      res.send(result);
    });
});

app.listen(PORT, () => {
  console.log(`Server listening on ${PORT}`, "0.0.0.0");
});
