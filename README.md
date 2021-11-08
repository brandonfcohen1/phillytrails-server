# Phillytrails Backend Server

This is a Node/Express App for [PhillyTrails](https://www.phillytrails.com).

The server performs 2 functions:
* Serves GeoJSON from my [PostGIS](https://postgis.net/) database. 
* Finds the center of a given route so the map can zoom there.

I wrote it originally for PostGIS 3, but since I am hosting on Heroku I had to rewrite for PostGIS 2.5 as [Heroku PostgreSQL only supports up to 2.5](https://devcenter.heroku.com/articles/postgis). The result is a bit messy but it works for now. my next step is to set up a tile service on this server instead of loading the entire GeoJSON at once, which will remove the need for this and increase performance.

I also plan on publishing guides to retrieve my data through a GeoJSON API shortly.

Please feel free to [get in touch](mailto:brandon.f.cohen@gmail.com) with any comments/questions/ideas. Also feel free to create issues and/or fork and make a PR.