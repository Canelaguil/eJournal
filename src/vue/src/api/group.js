import auth from '@/api/auth'

export default {
    create (data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.create('groups', data, connArgs)
            .then(response => response.data.group)
    },

    update (id, data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.update('groups/' + id, data, connArgs)
            .then(response => response.data.group)
    },

    delete (id, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.delete('groups/' + id, null, connArgs)
    },

    getAllFromCourse (cID, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.get('groups', {course_id: cID}, connArgs)
            .then(response => response.data.groups)
    }
}
