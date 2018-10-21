import * as types from '../constants/permission-types.js'
import router from '@/router'

const getters = {
    hasPermission: (state, getters, rootState, rootGetters) => (permission, givenKeyLevel = null, id = null) => {
        if (!rootGetters['user/loggedIn']) { return false }
        if ((!types.ALL_PERIMSSIONS.has(permission))) { throw Error('Permission input error, the requested permission: ' + permission + ' does not exist.') }
        if (givenKeyLevel && !types.PERMISSION_KEY_LEVELS.has(givenKeyLevel)) { throw Error('Permission input error, the requested key level does not exist.') }
        if (givenKeyLevel === 'general' && id) { throw Error('Permission input error, general permissions are without id.') }

        const permissions = rootGetters['user/permissions']
        const routeParams = router.currentRoute.params

        if (givenKeyLevel && id) {
            if (permissions[givenKeyLevel + id] === undefined) { throw Error('Permission type input error, no match for the given key: ' + givenKeyLevel + id + '.') }
            if (permissions[givenKeyLevel + id][permission] === undefined) { throw Error('Permission ' + permission + ' is not a valid permission for the context: ' + givenKeyLevel + id + '.') }
            return permissions[givenKeyLevel + id][permission]
        } else if (givenKeyLevel) {
            return permissions[givenKeyLevel][permission]
        } else if ('cID' in routeParams && types.COURSE_LEVEL_PERMISSIONS.has(permission)) {
            return permissions['course' + routeParams.cID][permission]
        } else if ('aID' in routeParams && types.ASSIGNMENT_LEVEL_PERMISSIONS.has(permission)) {
            return permissions['assignment' + routeParams.aID][permission]
        } else if (types.GENERAL_LEVEL_PERMISSIONS.has(permission)) {
            return permissions['general'][permission]
        } else {
            throw Error('Permission ' + permission + ' is not a valid permission for the context: {course' + routeParams.cID + ', assignment' + routeParams.aID + ', general}.')
        }
    }
}

export default {
    namespaced: true,
    getters
}
