import auth from '@/api/auth'

export default {
    get (id, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.get('journals/' + id, null, connArgs)
            .then(response => response.data.journal)
    },

    create (data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.create('journals', data, connArgs)
            .then(response => response.data.journal)
    },

    update (id, data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.update('journals/' + id, data, connArgs)
            .then(response => response.data.journal)
    },

    delete (id, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.delete('journals/' + id, null, connArgs)
            .then(response => response.data)
    },

    getNodes (id, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.get('nodes', {journal_id: id}, connArgs)
            .then(response => response.data.nodes)
    },

    getFromAssignment (cID, aID, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.get('journals', {course_id: cID, assignment_id: aID}, connArgs)
            .then(response => response.data.journals)
    }
}
