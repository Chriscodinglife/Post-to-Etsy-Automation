# Create A Local FastAPI Server to Automate posting a listing onto an Etsy Shop

## Purpose

During the Pandemic, I had lost my full time job. This prompted me to focus on growing as a programmer and as a designer, so I opened my own motion design store on Etsy. I noticed that posting to Etsy can be tedious work especially if I have plenty of designs to upload. 

So I wrote this server app that was originally written out in Flask with Python. Now I rewrote it in FastAPI which has been very intuitive and easy to migrate over. 

There are two scripts in this folder, one is the post_etsy_bot script that essentially runs selenium and a chromedriver, and there is the post_to_etsy_server script that opens a local server on the host that communicates with Etsy's API. 

This server was inspired by the Quick Start Tutorial from Etsy and their guide on how to create a local server with Javascript and Node. A link to that can be found here: [Etsy API Quick Start Tutorial](https://developers.etsy.com/documentation/tutorials/quickstart)

Although the Quick Start tutorial shows how to use the listing_r scope for Etsy, this server focuses on using the listing_w scope, and creating a draft Etsy Listing that can then be published within the Store settings. It was a little work to convert the Node logic over to Flask/FastAPI but eventually it worked out.

This script does the following:

- The server Directs the browser to the Etsy authorization endpoint requesting the user to authorize the app.
- The browser is redirected to an endpoint on the server that takes the token from Etsy
- The server then posts onto Etsy via the API with the API key and the Token credentials in order to make a draft on Etsy
- Finally the server uses Etsy's API to post all the images onto the Etsy listing


## TODO

Provide images and more insight to the server app!