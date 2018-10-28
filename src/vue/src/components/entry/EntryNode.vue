<!--
    Loads in an entry for a student, which was previously filled in
    by the student using an Add-Node or an empty Deadline-Entry-Node.
    It will also show the grade once it's published by responsible user
    and give a possibility to edit an entry if it still has the
    needed privileges.
 -->
<template>
    <div>
        <!-- Edit mode. -->
        <b-card v-if="saveEditMode == 'Save'" class="entry-card no-hover" :class="$root.getBorderClass(cID)">
            <div class="ml-2 btn float-right multi-form shadow no-hover" v-if="entryNode.entry.published">
                {{ entryNode.entry.grade }}
            </div>

            <h2 class="mb-2">{{ entryNode.entry.template.name }}</h2>
            <entry-fields
                :template="entryNode.entry.template"
                :completeContent="completeContent"
                :displayMode="false"
                :nodeID="entryNode.nID"
                :entryID="entryNode.entry.id"
            />

            <b-alert :show="dismissCountDown" dismissible variant="secondary"
                @dismissed="dismissCountDown=0">
                Some fields are empty or incorrectly formatted.
            </b-alert>
            <b-button class="add-button float-right mt-2" @click="saveEdit">
                <icon name="save"/>
                Save
            </b-button>
            <b-button class="delete-button mt-2" @click="cancel">
                <icon name="ban"/>
                Cancel
            </b-button>
        </b-card>
        <!-- Overview mode. -->
        <b-card v-else class="entry-card no-hover" :class="$root.getBorderClass(cID)">
            <div class="ml-2 grade-section shadow" v-if="entryNode.entry.published">
                <span class="grade">{{ entryNode.entry.grade }}</span>
            </div>
            <div class="ml-2 grade-section shadow" v-else-if="!entryNode.entry.editable">
                <icon name="hourglass-half"/>
            </div>
            <div v-else>
                <b-button v-if="entryNode.entry.editable" class="ml-2 delete-button float-right multi-form" @click="deleteEntry">
                    <icon name="trash"/>
                    Delete
                </b-button>
                <b-button v-if="entryNode.entry.editable" class="ml-2 change-button float-right multi-form" @click="saveEdit">
                    <icon name="edit"/>
                    Edit
                </b-button>
            </div>

            <h2 class="mb-2">{{ entryNode.entry.template.name }}</h2>
            <entry-fields
                :nodeID="entryNode.nID"
                :template="entryNode.entry.template"
                :completeContent="completeContent"
                :displayMode="true"
                :authorUID="$parent.journal.student.id"
                :entryID="entryNode.entry.id"
            />
            <div>
                <hr class="full-width"/>
                <span class="timestamp" v-if="entryNode.entry.last_edited">
                    Last edited: {{ $root.beautifyDate(entryNode.entry.last_edited) }}<br/>
                </span>
                <span class="timestamp" v-else>
                    Submitted on: {{ $root.beautifyDate(entryNode.entry.creation_date) }}<br/>
                </span>
            </div>
        </b-card>

        <comment-card :eID="entryNode.entry.id" :entryGradePublished="entryNode.entry.published"/>
    </div>
</template>

<script>
import commentCard from '@/components/journal/CommentCard.vue'
import icon from 'vue-awesome/components/Icon'
import entryFields from '@/components/entry/EntryFields.vue'

export default {
    props: ['entryNode', 'cID'],
    data () {
        return {
            saveEditMode: 'Edit',
            tempNode: this.entryNode,
            matchEntry: 0,
            completeContent: [],

            dismissSecs: 3,
            dismissCountDown: 0,
            showDismissibleAlert: false
        }
    },
    watch: {
        entryNode: function () {
            this.completeContent = []
            this.tempNode = this.entryNode
            this.saveEditMode = 'Edit'
            this.setContent()
        }
    },
    created () {
        this.setContent()
    },
    methods: {
        saveEdit: function () {
            if (this.saveEditMode === 'Save') {
                if (this.checkFilled()) {
                    this.saveEditMode = 'Edit'
                    this.tempNode.entry.content = this.completeContent
                    this.$emit('edit-node', this.tempNode)
                } else {
                    this.dismissCountDown = this.dismissSecs
                }
            } else {
                this.saveEditMode = 'Save'
                this.completeContent = []
                this.setContent()
            }
        },
        deleteEntry: function () {
            if (confirm('Are you sure that you want to delete this entry?')) {
                this.$emit('delete-node', this.tempNode)
            }
        },
        cancel: function () {
            this.saveEditMode = 'Edit'
            this.completeContent = []
            this.setContent()
        },
        setContent: function () {
            /* Loads in the data of an entry in the right order by matching
             * the different data-fields with the corresponding template-IDs. */
            var checkFound = false
            for (var templateField of this.entryNode.entry.template.field_set) {
                checkFound = false

                for (var content of this.entryNode.entry.content) {
                    if (content.field === templateField.id) {
                        this.completeContent.push({
                            data: content.data,
                            id: content.field,
                            contentID: content.id
                        })

                        checkFound = true
                        break
                    }
                }

                if (!checkFound) {
                    this.completeContent.push({
                        data: null,
                        id: templateField.id
                    })
                }
            }
        },
        checkFilled: function () {
            for (var i = 0; i < this.completeContent.length; i++) {
                var content = this.completeContent[i]
                var field = this.entryNode.entry.template.field_set[i]
                if (field.required && !content.data) {
                    return false
                }
            }

            return true
        }
    },
    components: {
        'comment-card': commentCard,
        'entry-fields': entryFields,
        icon
    }
}
</script>
