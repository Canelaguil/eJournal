<template>
    <b-card class="no-hover">
        <div v-for="a in assignments" :key="a.id">
            <div v-if="a.lti_couples">
                <assignment-card class="orange-border" @click.native="linkAssignment(a.id, a.lti_couples)" :assignment="a"/>
            </div>
            <div v-else>
                <assignment-card class="green-border" @click.native="linkAssignment(a.id, a.lti_couples)" :assignment="a"/>
            </div>
        </div>
    </b-card>
</template>

<script>
import assignmentCard from '@/components/assignment/AssignmentCard.vue'
import assignmentAPI from '@/api/assignment'

export default {
    name: 'LinkAssignment',
    props: ['lti', 'page'],
    components: {
        'assignment-card': assignmentCard
    },
    data () {
        return {
            assignments: []
        }
    },
    methods: {
        loadAssignments () {
            assignmentAPI.list(this.page.cID)
                .then(assignments => { this.assignments = assignments })
        },
        linkAssignment (aID, aLtiCouples) {
            if (!aLtiCouples || confirm('This assignment is already linked to ' + (aLtiCouples > 1 ? aLtiCouples + ' ' : 'an') + 'other assignment' + (aLtiCouples > 1 ? 's' : '') + ' from the learning-environment, are you sure you also want to link it?')) {
                assignmentAPI.update(aID, {lti_id: this.lti.ltiAssignID,
                    points_possible: this.lti.ltiPointsPossible,
                    is_published: this.lti.ltiAssignPublished,
                    unlock_date: this.lti.ltiAssignUnlock ? this.lti.ltiAssignUnlock.slice(0, -6) : null,
                    due_date: this.lti.ltiAssignDue ? this.lti.ltiAssignDue.slice(0, -6) : null,
                    lock_date: this.lti.ltiAssignLock ? this.lti.ltiAssignLock.slice(0, -6) : null})
                    .then(assignment => { this.$emit('handleAction', assignment.id) })
            }
        }
    },
    created () {
        this.loadAssignments()
    }
}
</script>
