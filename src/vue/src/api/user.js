import auth from '@/api/auth'

export default {

    get (id = 0) {
        return auth.get('users/' + id)
            .then(response => response.data.user)
    },

    create (data) {
        return auth.create('users', data)
            .then(response => response.data.user)
    },

    update (id = 0, data = null) {
        return auth.update('users/' + id, data)
            .then(response => response.data.user)
    },

    delete (id = 0) {
        return auth.delete('users/' + id)
            .then(response => response.data)
    },

    download (id = 0, fileName, entryID, nodeID, contentID) {
        return auth.downloadFile('users/' + id + '/download', {
            file_name: fileName,
            entry_id: entryID,
            node_id: nodeID,
            content_id: contentID
        })
    },

    GDPR (id = 0) {
        return auth.downloadFile('users/' + id + '/GDPR/')
    },

    /* Update user file. */
    uploadUserFile (data) {
        return auth.uploadFile('/users/upload/', data)
    },

    /* Upload an image. */
    uploadProfilePicture (data) {
        return auth.uploadFile('/users/upload_profile_picture/', data)
    },

    /* Downloads a profile picture */
    downloadProfilePicture (userID) {
        return auth.downloadFile('users/' + userID + '/download_profile_picture/', null, true)
    },

    /* Verify email adress using a given token. */
    verifyEmail (token) {
        return auth.post('/verify_email/', { token: token })
    },

    /* Request an email verification token for the given users email adress. */
    requestEmailVerification () {
        return auth.post('/request_email_verification/')
    }
}
