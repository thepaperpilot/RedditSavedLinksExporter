import util from './util'
import { combineReducers } from 'redux'

const loggedIn = util.createReducer(false, {
    'LOG_IN': () => true
})

const links = util.createReducer([], {
    'LOAD': (state, action) => action.links
})

const username = util.createReducer('', {
    'LOAD': (state, action) => action.username
})

export default combineReducers({
    loggedIn,
    links,
    username
})
