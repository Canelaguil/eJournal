import Vue from 'vue'
import * as types from '../constants/mutation-types.js'
import connection from '@/api/connection.js'
import genericUtils from '@/utils/generic_utils.js'
import sanitization from '@/utils/sanitization.js'

const getters = {
    jwtAccess: state => state.jwtAccess,
    jwtRefresh: state => state.jwtRefresh,
    uID: state => state.uID,
    username: state => state.username,
    email: state => state.email,
    verifiedEmail: state => state.verifiedEmail,
    profilePicture: state => state.profilePicture,
    firstName: state => state.firstName,
    lastName: state => state.lastName,
    ltiID: state => state.ltiID,
    gradeNotifications: state => state.gradeNotifications,
    commentNotifications: state => state.commentNotifications,
    permissions: state => state.permissions,
    loggedIn: state => state.jwtAccess !== null && state.uID !== null, // We are not logged unless the store is populated as well
    storePopulated: state => state.uID !== null
}

const mutations = {
    [types.SET_ACCES_TOKEN] (state, accessToken) {
        state.jwtAccess = accessToken
    },
    [types.SET_JWT] (state, data) {
        const access = data.access
        const refresh = data.refresh

        state.jwtAccess = access
        state.jwtRefresh = refresh
    },
    [types.HYDRATE_USER] (state, data) {
        const userData = data.user
        const permissions = data.user.permissions

        state.uID = userData.id
        state.username = userData.username
        state.email = userData.email
        state.verifiedEmail = userData.verified_email
        state.profilePicture = userData.profile_picture
        state.firstName = userData.first_name
        state.lastName = userData.last_name
        state.ltiID = userData.lti_id
        state.gradeNotifications = userData.grade_notifications
        state.commentNotifications = userData.comment_notifications
        state.permissions = permissions
    },
    [types.LOGOUT] (state) {
        state.jwtAccess = null
        state.jwtRefresh = null
        state.uID = null
        state.username = null
        state.email = null
        state.verifiedEmail = null
        state.profilePicture = null
        state.firstName = null
        state.lastName = null
        state.ltiID = null
        state.gradeNotifications = null
        state.commentNotifications = null
        state.permissions = null
    },
    [types.SET_GRADE_NOTIFICATION] (state, val) {
        state.gradeNotifications = val
    },
    [types.SET_COMMENT_NOTIFICATION] (state, val) {
        state.commentNotifications = val
    },
    [types.EMAIL_VERIFIED] (state) {
        state.verifiedEmail = true
    },
    [types.SET_FULL_USER_NAME] (state, data) {
        state.firstName = data.firstName
        state.lastName = data.lastName
    },
    [types.SET_PROFILE_PICTURE] (state, dataURL) {
        state.profilePicture = dataURL
    },
    [types.UPDATE_PERMISSIONS] (state, data) {
        const permissions = data.permissions
        const permissionKey = data.key

        state.permissions[permissionKey] = permissions
    }
}

const actions = {
    /* Authenticates the user and poplates the store, if either fails the login fails. */
    login ({ commit, dispatch }, { username, password }) {
        return new Promise((resolve, reject) => {
            connection.conn.post('/token/', {username: username, password: password}).then(response => {
                commit(types.SET_JWT, response.data)

                dispatch('populateStore').then(response => {
                    resolve('JWT and store are set successfully.')
                }, error => {
                    Vue.toasted.error(sanitization.escapeHtml(error.response.data.description))
                    reject(error) // Login success but hydration failed
                })
            }, error => {
                reject(error) // Login failed, hydration failed.
            })
        })
    },
    logout ({commit, state}) {
        return Promise.all([
            // Example how to access different module mutation: commit(`module/${types.MUTATION_TYPE}`, null, { root: true })
            commit(types.LOGOUT)
        ])
    },
    /* An attempt is made at refreshing the JW access token, store is populated if needed.
     * Fails if the refresh fails or if the store needed to be populated if that fails as well. */
    validateToken ({ commit, dispatch, getters }, error = null) {
        if (error) {
            var code
            if (error.response.data instanceof ArrayBuffer) {
                code = genericUtils.parseArrayBuffer(error.response.data).code
            } else {
                code = error.response.data.code
            }
        }

        return new Promise((resolve, reject) => {
            if (!error || code === 'token_not_valid') {
                connection.conn.post('token/refresh/', {refresh: getters.jwtRefresh}).then(response => {
                    commit(types.SET_ACCES_TOKEN, response.data.access) // Refresh token valid, update access token.

                    if (!getters.storePopulated) {
                        dispatch('populateStore')
                            .then(_ => { resolve() })
                            .catch(error => { reject(error) })
                    } else {
                        resolve('JWT refreshed successfully, store was already populated.')
                    }
                }, error => {
                    reject(error) // Refresh token invalid, reject
                })
            } else {
                reject(error) // We should not validate if the error has nothing to do with the token
            }
        })
    },
    populateStore ({ commit }) {
        return new Promise((resolve, reject) => {
            connection.conn.get('/users/0/').then(response => {
                commit(types.HYDRATE_USER, response.data)
                resolve('Store is populated successfully')
            }, error => {
                Vue.toasted.error(sanitization.escapeHtml(error.response.data.description))
                reject(error)
            })
        })
    }
}

export default {
    namespaced: true,
    state: {
        jwtAccess: null,
        jwtRefresh: null,
        uID: null,
        username: null,
        email: null,
        verifiedEmail: false,
        profilePicture: null,
        firstName: null,
        lastName: null,
        ltiID: null,
        gradeNotifications: null,
        commentNotifications: null,
        permissions: null
    },
    getters,
    mutations,
    actions
}
