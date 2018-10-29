<template>
    <b-card class="no-hover">
        <b-form @submit.prevent="onSubmit" @reset.prevent="onReset">
            <div class="d-flex float-right multi-form">
                <b-button v-if="form.isPublished" @click="form.isPublished = false" class="add-button flex-grow-1">
                    <icon name="check"/>
                    Published
                </b-button>
                <b-button v-if="!form.isPublished" @click="form.isPublished = true" class="delete-button flex-grow-1">
                    <icon name="times"/>
                    Unpublished
                </b-button>
            </div>

            <h2 class="field-heading">Assignment Name</h2>
            <b-input class="multi-form theme-input"
                v-model="form.assignmentName"
                placeholder="Assignment name"
                required
            />
            <h2 class="field-heading">Description</h2>
            <text-editor class="multi-form"
                :id="'text-editor-assignment-description'"
                :givenContent="'Description of the assignment'"
                @content-update="form.assignmentDescription = $event"
                :footer="false"
            />
            <h2 class="field-heading">Points possible</h2>
            <b-input class="multi-form theme-input"
            v-model="form.pointsPossible"
            placeholder="Points"
            type="number"/>
            <b-row>
                <b-col xl="4">
                    <h2 class="field-heading">Unlock date</h2>
                    <flat-pickr class="multi-form theme-input full-width"
                    v-model="form.unlockDate"
                    :config="$root.flatPickrTimeConfig"/>
                </b-col>
                <b-col xl="4">
                    <h2 class="field-heading">Due date</h2>
                    <flat-pickr class="multi-form theme-input full-width"
                    v-model="form.dueDate"
                    :config="$root.flatPickrTimeConfig"/>
                </b-col>
                <b-col xl="4">
                    <h2 class="field-heading">Lock date</h2>
                    <flat-pickr class="multi-form theme-input full-width"
                    v-model="form.lockDate"
                    :config="$root.flatPickrTimeConfig"/>
                </b-col>
            </b-row>
            <b-button class="float-left change-button mt-2" type="reset">
                <icon name="undo"/>
                Reset
            </b-button>
            <b-button class="float-right add-button mt-2" type="submit">
                <icon name="plus-square"/>
                Create
            </b-button>
        </b-form>
    </b-card>
</template>

<script>
import textEditor from '@/components/assets/TextEditor.vue'
import icon from 'vue-awesome/components/Icon'

import assignmentAPI from '@/api/assignment'

export default {
    name: 'CreateAssignment',
    props: ['lti', 'page'],
    data () {
        return {
            form: {
                assignmentName: '',
                assignmentDescription: '',
                courseID: '',
                ltiAssignID: null,
                pointsPossible: null,
                unlockDate: null,
                dueDate: null,
                lockDate: null,
                isPublished: false
            }
        }
    },
    components: {
        'text-editor': textEditor,
        icon
    },
    methods: {
        onSubmit () {
            assignmentAPI.create({
                name: this.form.assignmentName,
                description: this.form.assignmentDescription,
                course_id: this.form.courseID,
                lti_id: this.form.ltiAssignID,
                points_possible: this.form.pointsPossible,
                unlock_date: this.form.unlockDate,
                due_date: this.form.dueDate,
                lock_date: this.form.lockDate,
                is_published: this.form.isPublished
            })
                .then(assignment => {
                    this.$emit('handleAction', assignment.id)
                    this.onReset(undefined)
                    this.$store.dispatch('user/populateStore').catch(_ => {
                        this.$toasted.error('The website might be out of sync, please login again.')
                    })
                })
        },
        onReset (evt) {
            if (evt !== undefined) {
                evt.preventDefault()
            }
            /* Reset our form values */
            this.form.assignmentName = ''
            this.form.assignmentDescription = ''
            this.form.unlockDate = undefined
            this.form.dueDate = undefined
            this.form.lockDate = undefined
            this.form.isPublished = false

            /* Trick to reset/clear native browser form validation state */
            this.show = false
            this.$nextTick(() => { this.show = true })
        }
    },
    mounted () {
        if (this.lti !== undefined) {
            this.form.assignmentName = this.lti.ltiAssignName
            this.form.ltiAssignID = this.lti.ltiAssignID
            this.form.pointsPossible = this.lti.ltiPointsPossible
            this.form.unlockDate = this.lti.ltiAssignUnlock.slice(0, -9)
            this.form.dueDate = this.lti.ltiAssignDue.slice(0, -9)
            this.form.lockDate = this.lti.ltiAssignLock.slice(0, -9)
            this.form.courseID = this.page.cID
            this.form.isPublished = this.lti.ltiAssignPublished
        } else {
            this.form.courseID = this.$route.params.cID
        }
    }
}
</script>
