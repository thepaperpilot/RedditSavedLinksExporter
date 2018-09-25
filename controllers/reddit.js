const snoowrap = require('snoowrap')

exports.authenticate = async (req, res, next) => {
    try {
        const r = req.session.reddit = await snoowrap.fromAuthCode({
            code: req.body.code,
            userAgent: 'Reddit Saved Links Exporter by /u/thepaperpilot',
            clientId: process.env.REACT_APP_CLIENT_ID,
            clientSecret: process.env.CLIENT_SECRET,
            redirectUri: process.env.REACT_APP_REDIRECT_URI
        })
        const user = await r.getMe()
        user.getSavedContent({ limit: Infinity }).then(listings => {
            res.send({ links: listings, username: user.name })
        })
    } catch (e) {
        res.sendStatus(401)
    }
}
