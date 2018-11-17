<template>
    <div>
        <!-- TODO: This seems like an inappropriate permission check. Will have to be reconsidered in the rework. -->
        <b-card v-if="$hasPermission('can_add_course')" class="no-hover">
            <b-form-select v-model="selectedSortOption" :select-size="1">
                <option value="sortDate">Sort by date</option>
                <option value="sortNeedsMarking">Sort by marking needed</option>
            </b-form-select>
        </b-card>

        <div v-for="(d, i) in computedDeadlines" :key="i">
            <b-link v-if="d.course" tag="b-button" :to="assignmentRoute(d.course.id, d.id, d.journal, d.is_published)">
                <todo-card :deadline="d" :course="d.course" />
            </b-link>
            <b-link v-else v-for="(course, j) in d.courses" tag="b-button" :to="assignmentRoute(course.id, d.id, d.journal, d.is_published)"  :key="i + '-' + j">
                <todo-card :deadline="d" :course="course" />
            </b-link>
        </div>
    </div>
</template>

<script>
import todoCard from '@/components/assets/TodoCard.vue'
import todoSquare from '@/components/assets/TodoSquare.vue'

export default {
    props: ['deadlines'],
    data () {
        return {
            selectedSortOption: 'sortDate'
        }
    },
    components: {
        'todo-card': todoCard,
        'todo-square': todoSquare
    },
    methods: {
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
        }
    },
    computed: {
        computedDeadlines: function () {
            var counter = 0

            function compareDate (a, b) {
                if (!a.deadline) { return 1 }
                if (!b.deadline) { return -1 }
                return new Date(a.deadline) - new Date(b.deadline)
            }

            function compareMarkingNeeded (a, b) {
                if (a.stats.needs_marking + a.stats.unpublished > b.stats.needs_marking + b.stats.unpublished) { return -1 }
                if (a.stats.needs_marking + a.stats.unpublished < b.stats.needs_marking + b.stats.unpublished) { return 1 }
                return 0
            }

            function filterTop () {
                return (++counter <= 5)
            }

            function filterNoEntries (assignment) {
                return assignment.totalNeedsMarking !== 0
            }

            var deadlines = this.deadlines.slice()
            if (this.selectedSortOption === 'sortDate') {
                return deadlines.sort(compareDate).filter(filterTop)
            } else if (this.selectedSortOption === 'sortNeedsMarking') {
                return deadlines.sort(compareMarkingNeeded).filter(filterTop).filter(filterNoEntries)
            } else {
                return deadlines.sort(compareDate).filter(filterTop)
            }
        }
    }
}
</script>
