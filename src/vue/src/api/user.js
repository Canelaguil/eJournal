import auth from '@/api/auth'

export default {
    update (id, data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.update('users/' + id, data, connArgs)
            .then(response => response.data.user)
    },

    download (id, fileName, entryID, nodeID, contentID, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.downloadFile('users/' + id + '/download', {
            file_name: fileName,
            entry_id: entryID,
            node_id: nodeID,
            content_id: contentID
        }, connArgs)
    },

    GDPR (id, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.downloadFile('users/' + id + '/GDPR/', null, connArgs)
    },

    /* Update user file. */
    uploadUserFile (data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.uploadFile('/users/upload/', data, connArgs)
    },

    /* Upload an image. */
    uploadProfilePicture (data, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.uploadFile('/users/upload_profile_picture/', data, connArgs)
    },

    /* Downloads a profile picture */
    downloadProfilePicture (userID, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.downloadFile('users/' + userID + '/download_profile_picture/', null, connArgs)
    },

    /* Verify email adress using a given token. */
    verifyEmail (token, connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.post('/verify_email/', {token: token}, connArgs)
    },

    /* Request an email verification token for the given users email adress. */
    requestEmailVerification (connArgs = auth.DEFAULT_CONN_ARGS) {
        return auth.post('/request_email_verification/', null, connArgs)
    }
}
