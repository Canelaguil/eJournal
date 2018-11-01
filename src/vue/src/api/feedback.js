import auth from '@/api/auth'

export default {
    sendFeedback (data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.uploadFileEmail('/send_feedback/', data, connArgs)
    }
}
