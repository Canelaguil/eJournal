import auth from '@/api/auth'

export default {
    update (cID, data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.update('roles/' + cID, {roles: data}, connArgs)
            .then(response => response.data.role)
    },

    delete (cID, name, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.delete('roles/' + cID, {name: name}, connArgs)
            .then(response => response.data)
    },

    getFromCourse (id, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.get('roles', {course_id: id}, connArgs)
            .then(response => response.data.roles)
    }
}
