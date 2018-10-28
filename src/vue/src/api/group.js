import auth from '@/api/auth'

export default {

    create (data) {
        return auth.create('groups', data)
            .then(response => response.data.group)
    },

    update (id, data) {
        return auth.update('groups/' + id, data)
            .then(response => response.data.group)
    },

    delete (id) {
        return auth.delete('groups/' + id)
            .then(response => response.data)
    },

    getAllFromCourse (cID) {
        return auth.get('groups', {course_id: cID})
            .then(response => response.data.groups)
    }
}
