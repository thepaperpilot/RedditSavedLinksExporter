// Load environmental variables
require('dotenv').load({ path: '.env.local' })

// Imports
const bodyParser = require('body-parser')
const express = require('express')
const session = require('express-session')
const expressValidator = require('express-validator')
const lusca = require('lusca')
const path = require('path')

// Constants
const app = express()
const PORT = process.env.PORT || 8080

// Controllers (route handlers)
const redditController = require('./controllers/reddit')

// Express configuration
app.set('port', PORT)
app.use(bodyParser.urlencoded({extended: false}))
app.use(bodyParser.json())
app.use(session({ secret: process.env.APP_SECRET }))
app.use(expressValidator())
app.use(express.static(path.join(__dirname, 'public'), {maxAge: 31557600000}))

// Security :+1:
app.use(lusca.xframe('SAMEORIGIN'))
app.use(lusca.xssProtection(true))

// Routing
app.post('/auth', redditController.authenticate)

// Error page
app.use((err, req, res, next) => {
    // If the error object doesn't exists
    if (!err) return next()

    // Log it
    console.error(err.stack)

    // Send error message
    res.status(500)
})

// 404 page
app.use((req, res) => {
    res.status(404)
})

// Start server
app.listen(PORT, () => {
    console.log(`App listening on PORT: ${PORT}`)
})
