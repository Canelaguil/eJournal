import auth from '@/api/auth'

export default {

    get () {
        return auth.get('instance/0')
            .then(response => response.data.instance)
    },

    update (data) {
        return auth.update('instance/0', data)
            .then(response => response.data.instance)
    }

}
