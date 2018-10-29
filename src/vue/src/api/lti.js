import auth from '@/api/auth'

export default {
    /* Return te needed variables for course/assignment create, connect and select
     */
    getLtiParams (jwtParams, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.get('get_lti_params_from_jwt/' + jwtParams, null, connArgs)
            .then(response => response.data.params)
    }
}
