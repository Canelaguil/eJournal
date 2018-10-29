import auth from '@/api/auth'

export default {
    get (id, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.get('formats/' + id, null, connArgs)
            .then(response => response.data)
    },

    update (id, data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.update('formats/' + id, data, connArgs)
            .then(response => response.data)
    }
}
