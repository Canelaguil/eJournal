<!--
    Component that will show all the comments of a given entry and support
    the possibility to add comments when the right permissions are met.
-->
<template>
    <div>
        <div v-if="commentObject">
            <div v-for="(comment, index) in commentObject.entrycomments" class="comment-section" :key="index">
                <img class="profile-picture no-hover" :src="comment.author.picture">
                <b-card class="no-hover comment-card" :class="$root.getBorderClass($route.params.cID)">
                    <b-button v-if="authorData && authorData.uID == comment.author.uID" class="ml-2 delete-button float-right" @click="deleteComment(comment.ecID)">
                        <icon name="trash"/>
                        Delete
                    </b-button>
                    <span class="show-enters">{{ comment.text }}</span>
                    <hr/>
                    <b>{{ comment.author.first_name + ' ' + comment.author.last_name }}</b>
                    <span v-if="comment.published" class="timestamp">
                        {{ $root.beautifyDate(comment.timestamp) }}<br/>
                    </span>
                    <span v-else class="timestamp">
                        <icon name="hourglass-half" scale="0.8"/>
                        Will be published after grade<br/>
                    </span>
                </b-card>
            </div>
        </div>
        <div v-if="$root.canCommentJournal()" class="comment-section">
            <img class="profile-picture no-hover" :src="authorData.picture">
            <b-card class="no-hover new-comment">
                <b-textarea class="theme-input multi-form full-width" v-model="tempComment" placeholder="Write a comment" :class="$root.getBorderClass($route.params.cID)"/>
                <div class="d-flex full-width justify-content-end align-items-center">
                    <b-form-checkbox v-if="$root.canGradeJournal() && !entryGradePublished" v-model="publishAfterGrade" value=true unchecked-value=false>
                        Publish after grade
                    </b-form-checkbox>
                    <b-button class="send-button" @click="addComment">
                        <icon name="paper-plane"/>
                    </b-button>
                </div>
            </b-card>
        </div>
    </div>
</template>

<script>
import userApi from '@/api/user.js'
import entryApi from '@/api/entry.js'
import icon from 'vue-awesome/components/Icon'

export default {
    props: {
        eID: {
            required: true
        },
        entryGradePublished: {
            type: Boolean,
            default: false
        }
    },
    components: {
        icon
    },
    data () {
        return {
            tempComment: '',
            authorData: '',
            commentObject: null,
            publishAfterGrade: true
        }
    },
    watch: {
        eID () {
            this.tempComment = ''
            entryApi.getEntryComments(this.eID).then(response => { this.commentObject = response })
        },
        entryGradePublished () {
            entryApi.getEntryComments(this.eID).then(response => { this.commentObject = response })
        }
    },
    created () {
        this.getAuthorData()
        this.getEntryComments()
    },
    methods: {
        getAuthorData () {
            userApi.getOwnUserData()
                .then(response => { this.authorData = response })
        },
        getEntryComments () {
            entryApi.getEntryComments(this.eID)
                .then(response => {
                    this.commentObject = response
                })
        },
        addComment () {
            if (this.tempComment !== '') {
                entryApi.createEntryComment(this.eID, this.authorData.uID, this.tempComment, this.entryGradePublished, this.publishAfterGrade)
                    .then(_ => {
                        this.getEntryComments()
                        this.tempComment = ''
                    })
                    .catch(_ => { this.$toasted.error('Something went wrong whilst posting your comment, please try again!') })
            }
        },
        deleteComment (ecID) {
            if (confirm('Are you sure you want to delete this comment?')) {
                entryApi.deleteEntryComment(ecID)
                    .then(_ => { this.getEntryComments(this.eID) })
                    .catch(_ => { this.$toasted.error('Something went wrong whilst deleting the comment, please try again!') })
            }
        }
    }
}
</script>

<style lang="sass">
@import '~sass/modules/colors.sass'
.comment-section
    display: flex
    .profile-picture
        margin: 0px 12px
        display: inline
    .new-comment .card-body
        display: flex
        flex-wrap: wrap
    .card
        flex: 1 1 auto
        overflow: hidden
    .comment-card
        .card-body
            padding-bottom: 5px
        hr
            width: 120%
            margin-left: -10px !important
            border-color: $theme-dark-grey
            margin: 30px 0px 5px 0px
    .timestamp
        float: right
        font-family: 'Roboto Condensed', sans-serif
        color: grey
        svg
            fill: grey
</style>