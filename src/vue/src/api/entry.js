import auth from '@/api/auth'

export default {
    get (id, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.get('entries/' + id, null, connArgs)
            .then(response => response.data.entry)
    },

    create (data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.create('entries', data, connArgs)
            .then(response => response.data)
    },

    update (id, data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.update('entries/' + id, data, connArgs)
            .then(response => response.data.entry)
    },

    delete (id, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.delete('entries/' + id, null, connArgs)
            .then(response => response.data)
    },

    publish (id, published = true, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.update('entries/' + id, {published: published}, connArgs)
            .then(response => response.data.entry)
    }
}
