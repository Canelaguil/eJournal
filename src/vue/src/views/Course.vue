<template>
    <content-columns>
        <bread-crumb slot="main-content-column" @edit-click="handleEdit()"/>

        <div slot="main-content-column" v-for="a in assignments" :key="a.id">
            <b-link tag="b-button" :to="assignmentRoute(cID, a.id, a.journal, a.is_published)">
                <assignment-card :line1="a.name" :lti="a.lti_couples > 0" :published="a.is_published">
                    <b-button v-if="$hasPermission('can_delete_assignment')" @click.prevent.stop="deleteAssignment(a)" class="delete-button float-right">
                        <icon name="trash"/>
                        Delete
                    </b-button>
                </assignment-card>
            </b-link>
        </div>

        <b-button
            v-if="$hasPermission('can_add_assignment')"
            slot="main-content-column"
            @click="showModal('createAssignmentRef')"
            class="add-button grey-background full-width">
            <icon name="plus"/>
            Create New Assignment
        </b-button>

        <b-modal
            slot="main-content-column"
            ref="createAssignmentRef"
            title="Create new assignment"
            size="lg"
            hide-footer>
                <create-assignment @handleAction="handleCreated"/>
        </b-modal>

        <h3 slot="right-content-column">To Do</h3>
        <deadline-deck slot="right-content-column" :deadlines="deadlines"/>
    </content-columns>
</template>

<script>
import contentColumns from '@/components/columns/ContentColumns.vue'
import breadCrumb from '@/components/assets/BreadCrumb.vue'
import assignmentCard from '@/components/assignment/AssignmentCard.vue'
import todoCard from '@/components/assets/TodoCard.vue'
import mainCard from '@/components/assets/MainCard.vue'
import icon from 'vue-awesome/components/Icon'
import createAssignment from '@/components/assignment/CreateAssignment.vue'
import deadlineDeck from '@/components/assets/DeadlineDeck.vue'

import assignmentAPI from '@/api/assignment'

export default {
    name: 'Course',
    props: {
        cID: {
            required: true
        },
        courseName: String
    },
    data () {
        return {
            assignments: null,
            cardColor: '',
            post: null,
            error: null,
            deadlines: []
        }
    },
    components: {
        'content-columns': contentColumns,
        'bread-crumb': breadCrumb,
        'assignment-card': assignmentCard,
        'todo-card': todoCard,
        'main-card': mainCard,
        'create-assignment': createAssignment,
        'deadline-deck': deadlineDeck,
        icon
    },
    created () {
        this.loadAssignments()
    },
    methods: {
        loadAssignments () {
            assignmentAPI.getAllFromCourse(this.cID)
                .then(assignments => { this.assignments = assignments })
                .catch(error => { this.$toasted.error(error.response.data.description) })

            assignmentAPI.getUpcoming(this.cID)
                .then(deadlines => { this.deadlines = deadlines })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        customisePage () {
            this.$toasted.info('Wishlist: Customise page')
        },
        handleEdit () {
            this.$router.push({
                name: 'CourseEdit',
                params: {
                    cID: this.cID
                }
            })
        },
        handleCreated (aID) {
            this.$router.push({
                name: 'FormatEdit',
                params: {
                    cID: this.cID,
                    aID: aID
                }
            })
        },
        showModal (ref) {
            this.$refs[ref].show()
        },
        assignmentRoute (cID, aID, jID, isPublished) {
            var route = {
                params: {
                    cID: cID,
                    aID: aID
                }
            }

            if (!isPublished) {
                route.name = 'FormatEdit'
            } else if (this.$hasPermission('can_view_all_journals', 'assignment', aID)) {
                route.name = 'Assignment'
            } else {
                route.name = 'Journal'
                route.params.jID = jID
            }
            return route
        },
        deleteAssignment (assignment) {
            if (assignment.courses.length > 1
                ? confirm('Are you sure you want to remove this assignment from the course?')
                : confirm('Are you sure you want to delete this assignment?')) {
                assignmentAPI.delete(assignment.id, this.cID)
                    .then(_ => {
                        this.$toasted.success(assignment.courses.length > 1 ? 'Removed assignment.' : 'Deleted assignment.')
                        this.loadAssignments()
                    })
                    .catch(error => { this.$toasted.error(error.response.data.description) })
            }
        }
    }
}
</script>
